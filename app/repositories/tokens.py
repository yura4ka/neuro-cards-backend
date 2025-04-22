from app.models.token import TokenBase
from app.repositories.base import BaseRepository


class TokenRepository(BaseRepository):
    async def add_refresh_token(self, *, token: TokenBase, user_id: str) -> None:
        await self.db.execute(
            """
            INSERT INTO tokens (token, user_id, expires_at) VALUES (:token, :user_id, :expires_at)
            """,
            values={**token.model_dump(), "user_id": user_id},
        )
