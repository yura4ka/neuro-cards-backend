from datetime import datetime
from uuid import UUID
from app.models.card import CardBaseRequest
from app.models.core import CoreModel, DeckType, IDModelMixin


class DeckBase(CoreModel):
    title: str
    type: DeckType


class DeckCreateRequest(DeckBase):
    cards: list[CardBaseRequest]


class DeckPublic(DeckBase, IDModelMixin):
    created_at: datetime
    updated_at: datetime | None
    version: int
    user_id: UUID
