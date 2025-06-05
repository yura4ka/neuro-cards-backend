from datetime import datetime
from transformers import AutoTokenizer
from string import Template
from fastapi import HTTPException
import requests
from pydantic_core import from_json
import logging
from app.models.core import DeckType
from app.models.llm import (
    LMFlashCardResponse,
    LMGenerationCardResponse,
    LMQuizCardResponse,
)

logger = logging.getLogger("uvicorn.error")


flashcards_prompt = Template("""<start_of_turn>user
You are a helpful assistant that generates open-ended flashcard-style questions based on an input text."
Please extract important facts or concepts and generate a list of 1-3 questions for every paragraph in the following JSON format:
[
  {
    "question": "What is ...?",
    "answer": "It is a ..."
  },
  ...
]

Input:
${input}<end_of_turn>
<start_of_turn>model""")

quiz_prompt = Template("""<start_of_turn>user
You are a helpful assistant that generates multiple-choice questions based on an input text.
Please extract important facts or concepts and generate a list of 1-3 questions for every paragraph in the following JSON format:
[
  {
    "question": "What is ...?",
    "answers": ["Option A", "Option B", "Option C", "Option D"],
    "correctAnswer": 2,
    "difficulty": 1
  },
  ...
]
Where:
- `answers` always have 4 options.
- `correctAnswer` is a 0-based index in the `answers` array.
- `difficulty` is 0 (easy), 1 (medium), or 2 (hard), based on how hard the question is to answer from the input.

Input:
${input}<end_of_turn>
<start_of_turn>model""")


class LLMService:
    __model_name = "neuro-cards"
    __url = "http://localhost:11434/api/chat"
    __max_tokens = 4096

    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("unsloth/gemma-3-4b-it")
        self.__flashcards_prompt_len = len(
            self.tokenizer.tokenize(flashcards_prompt.template)
        )
        self.__quiz_prompt_len = len(self.tokenizer.tokenize(quiz_prompt.template))

    def __count_tokens(self, text: str):
        return len(self.tokenizer.tokenize(text))

    def __total_tokens(self, tokens: int, type: DeckType):
        return (
            tokens + self.__flashcards_prompt_len
            if type == DeckType.Flashcards
            else tokens + self.__quiz_prompt_len
        )

    def __chunk_text(self, text: str, type: DeckType) -> list[str]:
        paragraphs = [p.strip() for p in text.split("\n") if p.strip()]

        chunks = []
        current_chunk = ""
        current_tokens = 0

        for paragraph in paragraphs:
            paragraph_tokens = self.__count_tokens(paragraph)
            if (
                self.__total_tokens(current_tokens + paragraph_tokens, type)
                > self.__max_tokens
            ):
                chunks.append(current_chunk.strip())
                current_chunk = ""
                current_tokens = 0
            current_chunk += paragraph + "\n"
            current_tokens += paragraph_tokens

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    def __send_request(self, prompt: str) -> str:
        logger.info("===starting request===")
        payload = {
            "model": self.__model_name,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "raw": True,
            "options": {"seed": 2011},
        }
        response = requests.post(self.__url, json=payload)
        if response.status_code != 200:
            raise HTTPException(
                status_code=400,
                detail=[
                    {
                        "msg": "Error",
                        "status": response.status_code,
                        "err": response.text,
                    }
                ],
            )
        res = response.json()
        logger.info(res)
        return res["message"]["content"]

    def __generate_from_text(
        self, text: str, type: DeckType
    ) -> list[LMFlashCardResponse]:
        chunks = self.__chunk_text(text, type)
        result = []
        for c in chunks:
            formatted_prompt = (
                flashcards_prompt.substitute(input=c)
                if type == DeckType.Flashcards
                else quiz_prompt.substitute(input=c)
            )
            json_data = self.__send_request(formatted_prompt)
            json_data = json_data[json_data.index("[") : json_data.rindex("]") + 1]
            model = (
                LMFlashCardResponse
                if type == DeckType.Flashcards
                else LMQuizCardResponse
            )
            cards = [
                model.model_validate(c)
                for c in from_json(json_data, allow_partial=True)
            ]
            result.extend(cards)
        return result

    def generateCardsFromText(self, text: str) -> list[LMGenerationCardResponse]:
        cards = self.__generate_from_text(text, DeckType.Flashcards)
        return [
            LMGenerationCardResponse(
                question=cards[i].question,
                options=[cards[i].answer],
                correctAnswer=0,
                difficulty=0,
                tempId=round(datetime.now().timestamp() * (i + 0.5) * 1000),
            )
            for i in range(len(cards))
        ]

    def generateQuizFromText(self, text: str) -> list[str]:
        cards = self.__generate_from_text(text, DeckType.Quiz)
        return [
            LMGenerationCardResponse(
                question=cards[i].question,
                options=cards[i].answers,
                correctAnswer=cards[i].correctAnswer,
                difficulty=cards[i].difficulty,
                tempId=round(datetime.now().timestamp() * (i + 0.5) * 1000),
            )
            for i in range(len(cards))
        ]
