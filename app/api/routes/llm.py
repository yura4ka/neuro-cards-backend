from fastapi import APIRouter

from app.api.dependencies.auth import RequireAuthDependency
from app.api.dependencies.llm import LLMDependency
from app.models.llm import GenerateFromTextRequest, LMGenerationCardResponse
from app.models.core import DeckType


router = APIRouter()


@router.post("/generate-from-text")
async def generate_cards_from_text(
    request: GenerateFromTextRequest,
    llm: LLMDependency,
    user_id: RequireAuthDependency,
) -> list[LMGenerationCardResponse]:
    if request.type == DeckType.Flashcards:
        return llm.generateCardsFromText(text=request.text)
    else:
        return llm.generateQuizFromText(text=request.text)
