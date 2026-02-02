"""API v1 Router"""

from fastapi import APIRouter
from app.api.v1.endpoints import research, auth, config, documents, exports

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(research.router, prefix="/research", tags=["Research"])
api_router.include_router(documents.router, prefix="/documents", tags=["Documents"])
api_router.include_router(config.router, prefix="/config", tags=["Configuration"])
api_router.include_router(exports.router, prefix="/exports", tags=["Exports"])
