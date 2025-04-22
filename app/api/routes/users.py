from asyncpg import UniqueViolationError
from fastapi import APIRouter, HTTPException

from app.api.dependencies.repositories import (
    TokenRepositoryDependency,
    UserRepositoryDependency,
)
from app.models.token import TokenResponse
from app.models.user import CreateUserRequest, LoginRequest
from app.models.core import IDModelMixin
from app.services import auth_service


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


@router.post("/login")
async def login(
    request: LoginRequest,
    user_repository: UserRepositoryDependency,
    token_repository: TokenRepositoryDependency,
) -> TokenResponse:
    user = await user_repository.authenticate_user(request=request)
    if not user:
        raise HTTPException(status_code=401, detail=[{"msg": "Invalid credentials"}])
    access_token = auth_service.create_access_token(user=user)
    refresh_token = auth_service.create_refresh_token(user=user)

    await token_repository.add_refresh_token(token=refresh_token, user_id=user.id)

    return TokenResponse(
        access_token=access_token.token,
        refresh_token=refresh_token.token,
        access_token_expires_at=access_token.expires_at,
        refresh_token_expires_at=refresh_token.expires_at,
    )
