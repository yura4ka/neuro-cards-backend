from app.models.core import CoreModel, DeckType


class GenerateFromTextRequest(CoreModel):
    text: str
    type: DeckType


class LMQuizCardResponse(CoreModel):
    question: str
    answers: list[str]
    correctAnswer: int
    difficulty: int


class LMFlashCardResponse(CoreModel):
    question: str
    answer: str


class LMGenerationCardResponse(CoreModel):
    question: str
    options: list[str]
    correctAnswer: int
    difficulty: int
    tempId: int
