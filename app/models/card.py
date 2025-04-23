from app.models.core import CoreModel, DeckType


class CardBaseRequest(CoreModel):
    question: str
    options: list[str]
    correct_answer: int = 0
    difficulty: int = 0


class CardBase(CoreModel):
    type: DeckType
    question: str
    difficulty: int
    deck_id: str
