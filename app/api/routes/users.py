from asyncpg import UniqueViolationError
from fastapi import APIRouter, HTTPException
from app.api.dependencies.auth import RequireAuthDependency
from app.api.dependencies.repositories import UserRepositoryDependency
from app.models.user import CreateUserRequest, PublicUser
from app.models.core import IDModelMixin


router = APIRouter()


@router.post("/", status_code=201)
async def register_user(
    user: CreateUserRequest, user_repository: UserRepositoryDependency
) -> IDModelMixin:
    try:
        id = await user_repository.create_user(user)
    except UniqueViolationError:
        raise HTTPException(status_code=400, detail=[{"msg": "User already exists"}])
    return {"id": id}


@router.get("/")
async def get_current_user(
    user_id: RequireAuthDependency, user_repository: UserRepositoryDependency
) -> PublicUser:
    return await user_repository.get_user_by_id(user_id)
