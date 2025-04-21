from datetime import datetime
from app.models.core import CoreModel, IDModelMixin


class TokenBase(CoreModel):
    token: str
    expires_at: datetime


class RefreshTokenModel(IDModelMixin, TokenBase):
    user_id: str
    is_invalid: bool


class JWTMeta(CoreModel):
    iat: float = datetime.timestamp(datetime.now())
    exp: float


class JWTClaims(IDModelMixin):
    pass


class JWTPayload(JWTMeta, JWTClaims):
    pass


class TokenResponse(CoreModel):
    access_token: str
    refresh_token: str
    access_token_expires_at: float
    refresh_token_expires_at: float
