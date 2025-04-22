from asyncpg import UniqueViolationError
from fastapi import APIRouter, HTTPException

from app.api.dependencies.auth import RefreshTokenDependency
from app.api.dependencies.repositories import (
    TokenRepositoryDependency,
    UserRepositoryDependency,
)
from app.models.token import TokenResponse
from app.models.user import CreateUserRequest, LoginRequest
from app.models.core import IDModelMixin
from app.services import auth_service
from app.services.auth import AuthException


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


@router.post("/login", tags=["auth"])
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


@router.post("/refresh-tokens", tags=["auth"])
async def refresh_tokens(
    token: RefreshTokenDependency,
    user_repository: UserRepositoryDependency,
    token_repository: TokenRepositoryDependency,
) -> TokenResponse:
    is_token_valid = await token_repository.verify_refresh_token(
        token, user_id=token.user_id
    )
    if not is_token_valid:
        token_repository.invalidate_all_tokens(user_id=token.sub)
        raise AuthException

    user = await user_repository.get_user_by_id(token.sub)
    access_token = auth_service.create_access_token(user=user)
    refresh_token = auth_service.create_refresh_token(user=user)
    await token_repository.add_refresh_token(token=refresh_token, user_id=user.id)
    return TokenResponse(
        access_token=access_token.token,
        refresh_token=refresh_token.token,
        access_token_expires_at=access_token.expires_at,
        refresh_token_expires_at=refresh_token.expires_at,
    )
