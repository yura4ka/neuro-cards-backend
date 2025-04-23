from app.core.utils import get_total_items, update_values_from_page
from app.db.tables import (
    cards_table,
    decks_table,
    question_options_table,
    user_decks_table,
)
from app.models.card import CardPublic
from app.models.core import TotalItems
from app.models.deck import DeckCreateRequest, DeckPublic
from app.repositories.base import BaseRepository
import sqlalchemy as sa


class DeckRepository(BaseRepository):
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

            for card in deck.cards:
                card_result = await self.db.fetch_one(
                    cards_table.insert()
                    .values(
                        {
                            "type": deck.type,
                            "question": card.question,
                            "difficulty": card.difficulty,
                            "deck_id": result.id,
                        }
                    )
                    .returning(cards_table.c.id),
                )
                correct_answer_id: str | None = None
                for i, option in enumerate(card.options):
                    answer_result = await self.db.fetch_one(
                        question_options_table.insert()
                        .values({"card_id": card_result.id, "answer": option})
                        .returning(question_options_table.c.id),
                    )
                    if card.correct_answer == i:
                        correct_answer_id = answer_result.id
                await self.db.execute(
                    cards_table.update()
                    .where(cards_table.c.id == card_result.id)
                    .values({"correct_answer_id": correct_answer_id})
                )

            return result.id

    async def get_decks_by_user_id(self, *, user_id: str) -> list[DeckPublic]:
        result = await self.db.fetch_all(
            decks_table.select().where(decks_table.c.user_id == user_id)
        )
        return [DeckPublic(**deck) for deck in result]

    async def get_user_decks(self, *, user_id: str) -> list[DeckPublic]:
        result = await self.db.fetch_all(
            sa.select(
                user_decks_table.c["created_at", "updated_at"],
                decks_table.c["id", "title", "type", "version", "user_id"],
            )
            .join(decks_table, decks_table.c.id == user_decks_table.c.deck_id)
            .where(user_decks_table.c.user_id == user_id)
        )
        return [DeckPublic(**deck) for deck in result]

    async def get_deck_cards(
        self, *, deck_id: str, page: int | None
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
