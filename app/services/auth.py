from datetime import datetime, timedelta, timezone
import uuid
from fastapi import HTTPException
import jwt
from passlib.context import CryptContext

from app.core.config import settings
from app.models.token import JWTClaims, JWTMeta, JWTPayload, TokenBase
from app.models.user import UserModel

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=401,
            detail=[{"msg": "Could not validate token credentials."}],
            headers={"WWW-Authenticate": "Bearer"},
        )


class AuthService:
    def hash_password(self, *, password: str) -> str:
        return pwd_context.hash(password)

    def verify_password(self, *, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def __create_jwt_token(
        self, *, user: UserModel, secret_key: str, expires_in_minutes: int
    ) -> TokenBase:
        exp = datetime.now(timezone.utc) + timedelta(minutes=expires_in_minutes)
        id = uuid.uuid4()
        jwt_meta = JWTMeta(
            exp=exp,
            sub=str(user.id),
            jti=str(id),
        )
        jwt_claims = JWTClaims()
        token_payload = JWTPayload(
            **jwt_meta.model_dump(),
            **jwt_claims.model_dump(),
        )

        return TokenBase(
            token=jwt.encode(token_payload.model_dump(), secret_key, algorithm="HS256"),
            id=id,
            expires_at=exp,
        )

    def create_access_token(self, *, user: UserModel) -> TokenBase:
        return self.__create_jwt_token(
            user=user,
            secret_key=settings.access_token,
            expires_in_minutes=settings.access_token_expire_minutes,
        )

    def create_refresh_token(self, *, user: UserModel) -> TokenBase:
        return self.__create_jwt_token(
            user=user,
            secret_key=settings.refresh_token,
            expires_in_minutes=settings.refresh_token_expire_minutes,
        )

    def __decode_token(self, *, token: str, secret_key: str) -> JWTPayload:
        decoded_token = jwt.decode(token, secret_key, algorithms=["HS256"], verify=True)
        return JWTPayload(**decoded_token)

    def decode_access_token(self, token: str) -> JWTPayload:
        return self.__decode_token(token=token, secret_key=settings.access_token)

    def decode_refresh_token(self, token: str) -> JWTPayload:
        return self.__decode_token(token=token, secret_key=settings.refresh_token)
