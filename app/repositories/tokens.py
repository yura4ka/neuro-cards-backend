from app.models.token import TokenBase
from app.repositories.base import BaseRepository


class TokenRepository(BaseRepository):
    def add_refresh_token(self, *, token: TokenBase, user_id: str) -> None:
        self.db.execute(
            "INSERT INTO tokens (token, user_id) VALUES (:token, :user_id)",
            values={**token.model_dump(), "user_id": user_id},
        )
