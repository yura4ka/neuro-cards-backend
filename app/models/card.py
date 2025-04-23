from uuid import UUID

from pydantic import Json
from app.models.core import CoreModel, DeckType, IDModelMixin


class CardBaseRequest(CoreModel):
    question: str
    options: list[str]
    correct_answer: int = 0
    difficulty: int = 0


class CardBase(CoreModel):
    type: DeckType
    question: str
    difficulty: int
    deck_id: UUID


class QuestionOptionPublic(IDModelMixin):
    answer: str


class CardPublic(CardBase, IDModelMixin):
    correct_answer_id: UUID
    options: list[QuestionOptionPublic] | Json[list[QuestionOptionPublic]]
    is_deleted: bool
