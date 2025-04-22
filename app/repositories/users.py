from uuid import UUID
from databases import Database
from app.models.user import CreateUserRequest, LoginRequest, UserModel
from app.repositories.base import BaseRepository
from app.services import auth_service


class UserRepository(BaseRepository):
    def __init__(self, db: Database) -> None:
        super().__init__(db)
        self.auth_service = auth_service

    async def get_user_by_id(self, id: str) -> UserModel | None:
        user = await self.db.fetch_one(
            "SELECT * FROM users WHERE id = :id",
            values={"id": id},
        )
        if not user:
            return None
        return UserModel(**user)

    async def get_user_by_username(self, username: str) -> UserModel | None:
        user = await self.db.fetch_one(
            "SELECT * FROM users WHERE username = :username",
            values={"username": username},
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

    async def authenticate_user(self, *, request: LoginRequest) -> UserModel | None:
        user = await self.get_user_by_username(username=request.username)
        if not user:
            return None

        if not self.auth_service.verify_password(
            plain_password=request.password, hashed_password=user.password
        ):
            return None

        return user
