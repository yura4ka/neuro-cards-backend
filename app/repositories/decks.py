import asyncio
from datetime import datetime

from databases import Database
from fastapi import HTTPException
from app.core.utils import get_total_items, update_values_from_page
from app.db.tables import decks_table, user_decks_table

from app.models.card import (
    CardPublic,
    UserCardInfoBase,
    UserCardInfoPublic,
)
from app.models.core import TotalItems
from app.models.deck import (
    DeckCreateRequest,
    DeckPublic,
    DeckUpdateRequest,
    DeckWithCards,
)
from app.repositories.base import BaseRepository
import sqlalchemy as sa

from app.repositories.cards import CardRepository


class DeckRepository(BaseRepository):
    def __init__(self, db: Database) -> None:
        super().__init__(db)
        self.card_repository = CardRepository(db)

    async def get_deck_by_id(self, *, deck_id: str, user_id: str) -> DeckWithCards:
        deck = await self.get_user_decks(user_id=user_id, deck_id=deck_id)
        if (not deck) or len(deck) != 1:
            raise HTTPException(status_code=404, detail=[{"msg": "Not found"}])
        cards = await self.get_deck_cards(deck_id=deck_id)
        return DeckWithCards(cards=cards, **deck[0].model_dump())

    async def create_deck(self, *, deck: DeckCreateRequest, user_id: str) -> str:
        async with self.db.transaction():
            result = await self.db.fetch_one(
                decks_table.insert()
                .values(
                    {**deck.model_dump(exclude={"cards": True}), "user_id": user_id}
                )
                .returning(decks_table.c.id),
            )
            await self.db.execute(
                user_decks_table.insert().values(
                    {"deck_id": result.id, "user_id": user_id}
                )
            )

            await asyncio.create_task(
                self.card_repository.add_cards_to_deck(
                    connection=self.db.connection(),
                    deck_id=result.id,
                    deck_type=deck.type,
                    cards=deck.cards,
                )
            )

            return result.id

    async def get_decks_by_user_id(self, *, user_id: str) -> list[DeckPublic]:
        result = await self.db.fetch_all(
            decks_table.select().where(decks_table.c.user_id == user_id)
        )
        return [DeckPublic(**deck) for deck in result]

    async def get_user_decks(
        self, *, user_id: str, deck_id: str | None
    ) -> list[DeckPublic]:
        stmt = (
            sa.select(
                user_decks_table.c["created_at", "updated_at"],
                decks_table.c["id", "title", "type", "version", "user_id"],
            )
            .join(decks_table, decks_table.c.id == user_decks_table.c.deck_id)
            .where(user_decks_table.c.user_id == user_id)
        )
        if deck_id is not None:
            stmt = stmt.where(decks_table.c.id == deck_id)
        result = await self.db.fetch_all(stmt)
        return [DeckPublic(**deck) for deck in result]

    async def get_deck_cards(
        self, *, deck_id: str, page: int | None = None
    ) -> list[CardPublic]:
        result = await self.db.fetch_all(
            f"""
            SELECT c.*,
            json_agg(DISTINCT jsonb_build_object(
				'id', qo.id, 'answer', qo.answer
            )) AS options
            FROM cards AS c
            LEFT JOIN question_options AS qo ON c.id = qo.card_id
            WHERE c.deck_id = :deck_id
            GROUP BY c.id
            {"LIMIT :limit OFFSET :offset" if page is not None else ""}
            """,
            update_values_from_page(values={"deck_id": deck_id}, page=page),
        )
        return [CardPublic(**card) for card in result]

    async def get_total_cards(self, *, deck_id: str) -> TotalItems:
        result = await self.db.fetch_one(
            """
            SELECT COUNT(id) AS total
            FROM cards
            WHERE deck_id = :deck_id
            """,
            values={"deck_id": deck_id},
        )
        return get_total_items(total=result.total)

    async def get_deck_cards_from_version(
        self, *, deck_id: str, from_version: int, page: int | None
    ) -> list[CardPublic]:
        result = await self.db.fetch_all(
            f"""
            SELECT DISTINCT ON (c.id) c.*,
            json_agg(DISTINCT jsonb_build_object(
				'id', qo.id, 'answer', qo.answer
            )) AS options
            FROM deck_migrations AS m
            LEFT JOIN deck_migration_updates AS mu ON m.id = mu.deck_migration_id
            LEFT JOIN cards AS c ON mu.card_id = c.id
            LEFT JOIN question_options AS qo ON c.id = qo.card_id
            WHERE version > :from_version AND deck_id = :deck_id
            GROUP BY c.id
            {"LIMIT :limit OFFSET :offset" if page is not None else ""}
            """,
            update_values_from_page(
                values={"from_version": from_version, "deck_id": deck_id}, page=page
            ),
        )
        return [CardPublic(**card) for card in result]

    async def get_total_cards_from_version(
        self, *, deck_id: str, from_version: int
    ) -> TotalItems:
        result = await self.db.fetch_one(
            """
            SELECT COUNT(DISTINCT c.id) AS total
            FROM deck_migrations AS m
            LEFT JOIN deck_migration_updates AS mu ON m.id = mu.deck_migration_id
            LEFT JOIN cards AS c ON mu.card_id = c.id
            WHERE version > :from_version AND deck_id = :deck_id
            """,
            values={"from_version": from_version, "deck_id": deck_id},
        )
        return get_total_items(total=result.total)

    async def get_deck_card_info(
        self, *, user_id: str, deck_id: str, after_date: datetime
    ) -> list[UserCardInfoPublic]:
        result = await self.db.fetch_all(
            """
            SELECT uci.*,
            FROM cards AS c
            LEFT JOIN user_card_infos AS uci ON c.id = uci.card_id AND uci.user_id = :user_id
            WHERE c.deck_id = :deck_id AND
                (uci.updated_at >= :after_date OR uci.created_at >= :after_date)
            """,
            {
                "user_id": user_id,
                "deck_id": deck_id,
                "after_date": after_date,
            },
        )
        return [UserCardInfoPublic(**card) for card in result]

    async def update_card_info(
        self, *, user_id: str, deck_id: str, cards: list[UserCardInfoBase]
    ) -> None:
        async with self.db.transaction():
            for card in cards:
                await self.db.execute(
                    """
                    INSERT INTO user_card_info (user_id, card_id, 
                        last_answered_at, repetition_number, easiness_factor,
                        interval, is_learning, learning_step
                    )
                    VALUES (:user_id, :card_id,
                        :last_answered_at, :repetition_number, :easiness_factor,
                        :interval, :is_learning, :learning_step
                    )
                    ON CONFLICT (card_id, user_id) DO UPDATE
                    SET last_answered_at = :last_answered_at,
                        repetition_number = :repetition_number,
                        easiness_factor = :easiness_factor,
                        interval = :interval,
                        is_learning = :is_learning,
                        learning_step = :learning_step
                    """,
                    {
                        **card.model_dump(),
                        "user_id": user_id,
                    },
                )

            await self.db.execute(
                """
                UPDATE user_decks
                SET updated_at = now()
                WHERE user_id = :user_id AND deck_id = :deck_id
                """,
                {"user_id": user_id, "deck_id": deck_id},
            )

    async def update_deck(
        self, *, deck_id: str, user_id: str, deck: DeckUpdateRequest
    ) -> None:
        increase_version = deck.patch_cards or deck.deleted_cards
        async with self.db.transaction():
            deck_result = await self.db.execute(
                f"""
                UPDATE decks
                SET title = :title
                {", version = version + 1" if increase_version else ""}
                WHERE id = :deck_id AND user_id = :user_id
                RETURNING version, type
                """,
                {"title": deck.title, "deck_id": deck_id, "user_id": user_id},
            )
            if not increase_version:
                return
            migration_result = await self.db.fetch_one(
                """
                INSERT INTO deck_migrations (deck_id, version)
                VALUES (:deck_id, :version)
                RETURNING id
                """,
                {"deck_id": deck_id, "version": deck_result.version},
            )
            added_card_ids = await asyncio.create_task(
                self.card_repository.add_cards_to_deck(
                    connection=self.db.connection(),
                    deck_id=deck_id,
                    deck_type=deck_result.type,
                    cards=deck.new_cards,
                )
            )
            await asyncio.create_task(
                self.card_repository.mark_cards_as_deleted(
                    connection=self.db.connection(),
                    cards_id=deck.deleted_cards,
                    deck_id=deck_id,
                )
            )
            await asyncio.create_task(
                self.card_repository.update_cards(
                    connection=self.db.connection(),
                    cards=deck.update_cards,
                )
            )
            await asyncio.create_task(
                self.card_repository.create_card_migrations(
                    connection=self.db.connection(),
                    migration_id=migration_result.id,
                    cards_id=[
                        *added_card_ids,
                        *[c.id for c in deck.update_cards],
                        *deck.deleted_cards,
                    ],
                )
            )
