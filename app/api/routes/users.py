from asyncpg import UniqueViolationError
from fastapi import APIRouter, HTTPException
from app.api.dependencies.repositories import UserRepositoryDependency
from app.models.user import CreateUserRequest
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
