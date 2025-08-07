from fastapi import APIRouter
from . import health, analytics

# Import other endpoint modules as they are created
# from . import users, etc.

api_router = APIRouter(prefix="/v1")

# Include routers
api_router.include_router(health.router)
# api_router.include_router(fingerprints.router)
api_router.include_router(analytics.router)

# Add other routers as they are created
# api_router.include_router(users.router)
