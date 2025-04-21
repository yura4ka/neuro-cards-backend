from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthException(BaseException):
    pass


class AuthService:
    def hash_password(self, *, password: str) -> str:
        return pwd_context.hash(password)
