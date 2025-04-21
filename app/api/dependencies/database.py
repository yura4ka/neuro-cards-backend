from typing import Annotated, Callable, Type
from databases import Database

from fastapi import Depends
from starlette.requests import Request

from app.repositories.base import BaseRepository


def get_database(request: Request) -> Database:
    return request.app.state._db


def get_repository(Repo: Type[BaseRepository]) -> Callable:
    def get_repo(
        db: Annotated[Database, Depends(get_database)],
    ) -> Type[BaseRepository]:
        return Repo(db)

    return get_repo
