from datetime import datetime, timezone
from app.models.core import CoreModel, IDModelMixin


class TokenBase(CoreModel):
    token: str
    expires_at: datetime


class RefreshTokenModel(IDModelMixin, TokenBase):
    user_id: str
    is_invalid: bool


class JWTMeta(CoreModel):
    iat: datetime = datetime.now(timezone.utc)
    exp: datetime


class JWTClaims(CoreModel):
    id: str


class JWTPayload(JWTMeta, JWTClaims):
    pass


class TokenResponse(CoreModel):
    access_token: str
    refresh_token: str
    access_token_expires_at: datetime
    refresh_token_expires_at: datetime
