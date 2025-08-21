from fastapi import APIRouter
from . import feedback, social_media, webhooks, utils, users

# Create the main API router with /api prefix
api_router = APIRouter(prefix="/api")

# Include all API modules
api_router.include_router(feedback.router)
api_router.include_router(social_media.router)
api_router.include_router(webhooks.router)
api_router.include_router(utils.router)
api_router.include_router(users.router)
