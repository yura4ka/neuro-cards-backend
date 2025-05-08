import asyncio
from databases.core import Connection
from app.db.tables import cards_table, question_options_table
from app.models.card import CardCreateRequest, CardUpdateRequest
from app.repositories.base import BaseRepository


class CardRepository(BaseRepository):
    async def add_question_options(
        self, *, connection: Connection, card: CardUpdateRequest
    ) -> str:
        correct_answer_id: str | None = None
        for i, option in enumerate(card.options):
            answer_result = await connection.fetch_one(
                question_options_table.insert()
                .values({"card_id": card.id, "answer": option})
                .returning(question_options_table.c.id),
            )
            if card.correct_answer == i:
                correct_answer_id = answer_result.id
        await connection.execute(
            cards_table.update()
            .where(cards_table.c.id == card.id)
            .values({"correct_answer_id": correct_answer_id})
        )

    async def add_cards_to_deck(
        self,
        *,
        connection: Connection,
        deck_id: str,
        deck_type: str,
        cards: list[CardCreateRequest],
    ) -> list[str]:
        result: list[str] = []
        for card in cards:
            card_result = await connection.fetch_one(
                cards_table.insert()
                .values(
                    {
                        "type": deck_type,
                        "question": card.question,
                        "difficulty": card.difficulty,
                        "deck_id": deck_id,
                    }
                )
                .returning(cards_table.c.id),
            )
            result.append(card_result.id)
            await asyncio.create_task(
                self.add_question_options(
                    connection=connection,
                    card=CardUpdateRequest(id=card_result.id, **card.model_dump()),
                )
            )

    async def create_card_migrations(
        self, *, connection: Connection, migration_id: str, cards_id: list[str]
    ) -> None:
        await connection.execute_many(
            """
            INSERT INTO deck_migration_updates (deck_migration_id, card_id)
            VALUES (:migration_id, :card_id)
            """,
            [
                {"migration_id": migration_id, "card_id": card_id}
                for card_id in cards_id
            ],
        )

    async def mark_cards_as_deleted(
        self, *, connection: Connection, cards_id: list[str], deck_id: str
    ) -> None:
        await connection.execute_many(
            cards_table.update()
            .where(cards_table.c.id.in_(cards_id), cards_table.c.deck_id == deck_id)
            .values({"is_deleted": True}),
        )

    async def update_card_options(
        self, *, connection: Connection, card: CardUpdateRequest
    ) -> None:
        await connection.execute(
            question_options_table.delete().where(
                question_options_table.c.card_id == card.id
            )
        )
        await asyncio.create_task(
            self.add_question_options(connection=connection, card=card)
        )

    async def update_cards(
        self, *, connection: Connection, cards: list[CardUpdateRequest]
    ) -> None:
        for card in cards:
            await connection.execute(
                cards_table.update()
                .where(cards_table.c.id == card.card_id)
                .values(
                    question=card.question,
                    difficulty=card.difficulty,
                    correct_answer_id=card.correct_answer_id,
                )
            )
            await asyncio.create_task(
                self.update_card_options(connection=connection, card=card)
            )
