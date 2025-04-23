from app.db.tables import (
    cards_table,
    decks_table,
    question_options_table,
    user_decks_table,
)
from app.models.deck import DeckCreateRequest
from app.repositories.base import BaseRepository


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
