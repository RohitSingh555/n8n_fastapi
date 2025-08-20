from fastapi import APIRouter
from . import feedback, social_media, webhooks, utils

# Create the main API router
api_router = APIRouter()

# Include all API modules
api_router.include_router(feedback.router)
api_router.include_router(social_media.router)
api_router.include_router(webhooks.router)
api_router.include_router(utils.router)
