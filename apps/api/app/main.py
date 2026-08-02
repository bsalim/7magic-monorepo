import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.dependencies import AuthError
from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.errors import error_response

settings = get_settings()

# Uvicorn configures only its own loggers, so the app's warnings -- a missing
# RESEND_API_KEY, a failed R2 upload -- would go to a logger with no handler and
# vanish. basicConfig() is not enough: it is a no-op once uvicorn has installed a
# root handler, so attach a handler to the "app" logger directly.
_app_logger = logging.getLogger("app")
if not _app_logger.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(logging.Formatter("%(levelname)s:%(name)s:%(message)s"))
    _app_logger.addHandler(_handler)
_app_logger.setLevel(logging.INFO)
# Already emitted through our own handler; let uvicorn's root stay clean.
_app_logger.propagate = False

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AuthError)
async def auth_error_handler(_, error: AuthError):
    return error_response(
        status_code=error.status_code,
        code=error.code,
        message=error.message,
    )


app.include_router(api_router, prefix=settings.api_v1_prefix)
