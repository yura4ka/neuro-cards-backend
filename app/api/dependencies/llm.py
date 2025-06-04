from typing import Annotated

from fastapi import Depends
from app.services.llm import LLMService
from app.services import llm_service


def get_llm() -> LLMService:
    return llm_service


LLMDependency = Annotated[LLMService, Depends(get_llm)]
