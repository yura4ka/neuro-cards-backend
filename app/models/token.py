from datetime import datetime, timezone
from app.models.core import CoreModel, IDModelMixin


class TokenBase(IDModelMixin):
    token: str
    expires_at: datetime


class RefreshTokenModel(TokenBase):
    user_id: str
    is_invalid: bool


class JWTMeta(CoreModel):
    iat: datetime = datetime.now(timezone.utc)
    exp: datetime
    jti: str
    sub: str


class JWTClaims(CoreModel):
    pass


class JWTPayload(JWTMeta, JWTClaims):
    pass


class TokenResponse(CoreModel):
    access_token: str
    refresh_token: str
    access_token_expires_at: datetime
    refresh_token_expires_at: datetime

class ParsedToken(JWTPayload):
    token_str: str