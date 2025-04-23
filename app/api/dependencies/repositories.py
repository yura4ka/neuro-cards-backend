from typing import Annotated

from fastapi import Depends
from app.api.dependencies.database import get_repository
from app.repositories.decks import DeckRepository
from app.repositories.tokens import TokenRepository
from app.repositories.users import UserRepository


UserRepositoryDependency = Annotated[
    UserRepository, Depends(get_repository(UserRepository))
]

TokenRepositoryDependency = Annotated[
    TokenRepository, Depends(get_repository(TokenRepository))
]

DeckRepositoryDependency = Annotated[
    DeckRepository, Depends(get_repository(DeckRepository))
]
