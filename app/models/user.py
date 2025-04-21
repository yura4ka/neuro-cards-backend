import datetime
from typing import Self
from pydantic import Field, EmailStr, model_validator
from app.models.core import CoreModel, IDModelMixin


class UserModel(IDModelMixin):
    created_at: datetime.datetime
    username: str
    email: str
    password: str
    restoration_code: str | None
    restoration_expires_at: datetime.datetime | None
    last_restoration_at: datetime.datetime | None
    restoration_attempts: int


class CreateUserRequest(CoreModel):
    username: str = Field(min_length=3, max_length=64)
    email: EmailStr
    password: str = Field(min_length=8)
    confirm_password: str

    @model_validator(mode="after")
    def check_passwords_match(self) -> Self:
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self


class LoginRequest(CoreModel):
    username: str
    password: str
