from enum import Enum
from typing import Generic, TypeVar
import uuid
from pydantic import BaseModel


class CoreModel(BaseModel):
    pass


class IDModelMixin(BaseModel):
    id: uuid.UUID


class StatusResponse(CoreModel):
    status: str


class TotalItems(CoreModel):
    total_items: int
    total_pages: int


class ResponseMeta(TotalItems):
    pass


T = TypeVar("T", bound=CoreModel)


class ResponseWithPagination(BaseModel, Generic[T]):
    items: list[T]
    meta: ResponseMeta


class DeckType(str, Enum):
    Flashcards = "Flashcards"
    Quiz = "Quiz"
