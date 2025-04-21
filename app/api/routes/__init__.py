from fastapi import APIRouter

from app.api.routes.testing import router as testing_router


router = APIRouter()
router.include_router(testing_router, prefix="/testing", tags=["cleanings"])
