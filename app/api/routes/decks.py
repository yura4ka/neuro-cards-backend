from uuid import UUID
from fastapi import APIRouter
from app.api.dependencies.auth import RequireAuthDependency
from app.api.dependencies.repositories import DeckRepositoryDependency
from app.models.card import CardPublic
from app.models.deck import DeckCreateRequest, DeckPublic
from app.models.core import IDModelMixin, ResponseMeta, ResponseWithPagination


router = APIRouter()


@router.post("/", status_code=201)
async def create_deck(
    new_deck: DeckCreateRequest,
    user_id: RequireAuthDependency,
    deck_repository: DeckRepositoryDependency,
) -> IDModelMixin:
    id = await deck_repository.create_deck(deck=new_deck, user_id=user_id)
    return {"id": id}


@router.get("/")
async def get_created_decks(
    user_id: RequireAuthDependency,
    deck_repository: DeckRepositoryDependency,
) -> list[DeckPublic]:
    return await deck_repository.get_decks_by_user_id(user_id=user_id)


@router.get("/user-decks")
async def get_user_decks(
    user_id: RequireAuthDependency, deck_repository: DeckRepositoryDependency
) -> list[DeckPublic]:
    return await deck_repository.get_user_decks(user_id=user_id)


@router.get("/{deck_id}/cards")
async def get_deck_cards(
    deck_id: UUID,
    user_id: RequireAuthDependency,
    deck_repository: DeckRepositoryDependency,
    from_version: int | None = None,
    page: int | None = None,
) -> ResponseWithPagination[CardPublic]:
    if from_version is not None:
        cards = await deck_repository.get_deck_cards_from_version(
            deck_id=deck_id, from_version=from_version, page=page
        )
        total = await deck_repository.get_total_cards_from_version(
            deck_id=deck_id, from_version=from_version
        )
        return ResponseWithPagination(items=cards, meta=ResponseMeta(**total))

    cards = await deck_repository.get_deck_cards(deck_id=deck_id, page=page)
    total = await deck_repository.get_total_cards(deck_id=deck_id)
    return ResponseWithPagination(items=cards, meta=ResponseMeta(**total.model_dump()))
