"""Primitives shared by the admin routers.

Add a helper here only once three or more routers need it. The source platform's
equivalent file carried that same threshold and it is the reason the split held.

`branch_scope` is the one piece every branch-aware route depends on: it resolves
the caller's grants into an AccessSet, so a router never reads role rows itself.
"""

from __future__ import annotations

from datetime import datetime
from typing import Annotated

from fastapi import Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import require_admin_user
from app.core.database import get_db_session
from app.core.errors import error_response
from app.domains.branches.access import AccessSet, access_set_for
from app.services.auth import AuthenticatedUser

DbSession = Annotated[AsyncSession, Depends(get_db_session)]
CurrentUser = Annotated[AuthenticatedUser, Depends(require_admin_user)]


def branch_scope(user: CurrentUser) -> AccessSet:
    return access_set_for(user.branch_grants)


BranchScope = Annotated[AccessSet, Depends(branch_scope)]


def iso(value: datetime | None) -> str | None:
    return value.isoformat() if value else None


def forbidden_branch():
    return error_response(
        status_code=status.HTTP_403_FORBIDDEN,
        code="branch_forbidden",
        message="You do not have access to this branch.",
    )


def not_found(code: str, message: str):
    return error_response(status_code=status.HTTP_404_NOT_FOUND, code=code, message=message)


def conflict(code: str, message: str):
    return error_response(status_code=status.HTTP_409_CONFLICT, code=code, message=message)
