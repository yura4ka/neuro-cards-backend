from datetime import datetime
from uuid import UUID
from app.models.card import CardCreateRequest, CardUpdateRequest
from app.models.core import CoreModel, DeckType, IDModelMixin


class DeckBase(CoreModel):
    title: str
    type: DeckType


class DeckCreateRequest(DeckBase):
    cards: list[CardCreateRequest]


class DeckPublic(DeckBase, IDModelMixin):
    created_at: datetime
    updated_at: datetime | None
    version: int
    user_id: UUID


class DeckUpdateRequest(CoreModel):
    title: str
    new_cards: list[CardCreateRequest]
    update_cards: list[CardUpdateRequest]
    deleted_cards: list[UUID]
