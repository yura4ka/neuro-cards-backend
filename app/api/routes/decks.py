from fastapi import APIRouter
from app.api.dependencies.auth import RequireAuthDependency
from app.api.dependencies.repositories import DeckRepositoryDependency
from app.models.deck import DeckCreateRequest
from app.models.core import IDModelMixin


router = APIRouter()


@router.post("/", status_code=201)
async def create_deck(
    new_deck: DeckCreateRequest,
    user_id: RequireAuthDependency,
    deck_repository: DeckRepositoryDependency,
) -> IDModelMixin:
    id = await deck_repository.create_deck(deck=new_deck, user_id=user_id)
    return {"id": id}
