from fastapi import APIRouter
from app.api.v1.routes.auth import router as auth_router
from app.api.v1.routes.polish import router as polish_router
from app.api.v1.routes.feedback import router as feedback_router  # ✅ add

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth_router)
api_router.include_router(polish_router)
api_router.include_router(feedback_router)  # ✅ add
