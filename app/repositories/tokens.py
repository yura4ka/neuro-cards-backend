from app.models.token import ParsedToken, TokenBase
from app.repositories.base import BaseRepository


class TokenRepository(BaseRepository):
    async def add_refresh_token(self, *, token: TokenBase, user_id: str) -> None:
        await self.db.execute(
            """
            INSERT INTO tokens (id, token, user_id, expires_at) 
            VALUES (:id, :token, :user_id, :expires_at)
            """,
            values={**token.model_dump(), "user_id": user_id},
        )

    async def verify_refresh_token(self, token: ParsedToken) -> bool:
        result = await self.db.fetch_one(
            """
            SELECT is_invalid FROM tokens 
            WHERE token = :token AND user_id = :user_id and id = :id
            """,
            values={"token": token.token_str, "user_id": token.sub, "id": token.jti},
        )
        return bool(result) and not result.is_invalid

    async def invalidate_refresh_token(self, *, id: str) -> None:
        await self.db.execute(
            "UPDATE tokens SET is_invalid = true WHERE id = :id",
            values={"id": id},
        )

    async def invalidate_all_tokens(self, *, user_id: str) -> None:
        await self.db.execute(
            "UPDATE tokens SET is_invalid = true WHERE user_id = :user_id",
            values={"user_id": user_id},
        )
