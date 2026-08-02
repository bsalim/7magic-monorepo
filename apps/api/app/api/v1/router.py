from fastapi import APIRouter

from app.api.v1.endpoints import admin, auth, health, public, venues

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(public.router, prefix="/public", tags=["public"])
api_router.include_router(venues.router, prefix="/venues", tags=["venues"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
