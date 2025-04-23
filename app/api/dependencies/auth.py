from typing import Annotated
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from app.models.token import ParsedToken
from app.services import auth_service
from app.services.auth import AuthException


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/users/login/")


async def require_auth(token: Annotated[str, Depends(oauth2_scheme)]) -> str:
    try:
        decoded = auth_service.decode_access_token(token=token)
        return decoded.sub
    except Exception:
        raise AuthException


async def require_refresh_token(
    token: Annotated[str, Depends(oauth2_scheme)],
) -> ParsedToken:
    try:
        decoded = auth_service.decode_refresh_token(token=token)
        return ParsedToken(**decoded.model_dump(), token_str=token)
    except Exception:
        raise AuthException


RequireAuthDependency = Annotated[str, Depends(require_auth)]
RefreshTokenDependency = Annotated[ParsedToken, Depends(require_refresh_token)]
