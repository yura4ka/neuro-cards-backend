from datetime import datetime
from string import Template
from fastapi import HTTPException
import requests
from pydantic_core import from_json
import logging
from app.models.llm import LMFlashCardResponse, LMGenerationCardResponse

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
<start_of_turn>model
""")


class LLMService:
    __model_name = "neuro-cards"
    __url = "http://localhost:11434/api/chat"

    def send_request(self, prompt: str) -> str:
        logger.info("===starting request===")
        payload = {
            "model": self.__model_name,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
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

    def generateCardsFromText(self, text: str) -> list[LMGenerationCardResponse]:
        formatted_prompt = flashcards_prompt.substitute(input=text)
        json_data = self.send_request(formatted_prompt)
        json_data = json_data[json_data.index("[") : json_data.rindex("]") + 1]

        try:
            cards = [
                LMFlashCardResponse.model_validate(c)
                for c in from_json(json_data, allow_partial=True)
            ]
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
        except Exception:
            raise HTTPException(
                status_code=400,
                detail=[
                    {
                        "msg": "Error",
                    }
                ],
            )

    def generateQuizFromText(self, text: str) -> list[str]:
        return []
