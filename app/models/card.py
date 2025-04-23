from datetime import datetime
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


class UserCardInfoBase(CoreModel):
    card_id: UUID
    last_answered_at: datetime
    repetition_number: int
    easiness_factor: float
    interval: float
    is_learning: bool
    learning_step: int


class UserCardInfoPublic(UserCardInfoBase):
    user_id: UUID
    created_at: datetime
    updated_at: datetime | None
