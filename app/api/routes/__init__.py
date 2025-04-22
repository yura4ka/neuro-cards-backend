from fastapi import APIRouter

from app.api.routes.users import router as users_router
from app.api.routes.auth import router as auth_router


router = APIRouter()
router.include_router(auth_router, prefix="/auth", tags=["auth"])
router.include_router(users_router, prefix="/users", tags=["users"])
