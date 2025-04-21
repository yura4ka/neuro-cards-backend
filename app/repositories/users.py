from uuid import UUID
from databases import Database
from app.models.users import CreateUserRequest, UserModel
from app.repositories.base import BaseRepository
from app.services import auth_service
import sqlalchemy as sa


class UserRepository(BaseRepository):
    def __init__(self, db: Database) -> None:
        super().__init__(db)
        self.auth_service = auth_service

    async def get_user_by_email(self, email: str) -> UserModel | None:
        user = await self.db.fetch_one(
            sa.select(UserModel).where(UserModel.email == email)
        )
        if not user:
            return None
        return UserModel(**user)

    async def create_user(self, user: CreateUserRequest) -> UUID:
        hashed_password = self.auth_service.hash_password(password=user.password)
        result = await self.db.fetch_one(
            """
            INSERT INTO users (username, email, password) 
            VALUES (:username, :email, :password) 
            RETURNING id;
            """,
            user.model_copy(update={"password": hashed_password}).model_dump(
                exclude={"confirm_password": True}
            ),
        )
        return result.id
