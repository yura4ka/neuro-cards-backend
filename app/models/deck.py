from app.models.card import CardBaseRequest
from app.models.core import CoreModel, DeckType


class DeckCreateRequest(CoreModel):
    title: str
    type: DeckType
    cards: list[CardBaseRequest]
