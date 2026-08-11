from fastapi import APIRouter, Depends

from app.api.v1.admin import branches as admin_branches
from app.api.v1.admin import event_emails as admin_event_emails
from app.api.v1.admin import event_registrations as admin_event_registrations
from app.api.v1.admin import events as admin_events
from app.api.v1.dependencies import require_admin_user
from app.api.v1.endpoints import admin, auth, health, public, venues

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(public.router, prefix="/public", tags=["public"])
api_router.include_router(venues.router, prefix="/venues", tags=["venues"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])

# The per-resource admin routers. `admin` above is app.api.v1.endpoints.admin;
# these come from the app.api.v1.admin package, hence the aliases.
api_router.include_router(
    admin_branches.router,
    prefix="/admin",
    tags=["admin-branches"],
    dependencies=[Depends(require_admin_user)],
)
api_router.include_router(
    admin_events.router,
    prefix="/admin",
    tags=["admin-events"],
    dependencies=[Depends(require_admin_user)],
)
api_router.include_router(
    admin_event_registrations.router,
    prefix="/admin",
    tags=["admin-event-registrations"],
    dependencies=[Depends(require_admin_user)],
)
api_router.include_router(
    admin_event_emails.router,
    prefix="/admin",
    tags=["admin-event-emails"],
    dependencies=[Depends(require_admin_user)],
)
