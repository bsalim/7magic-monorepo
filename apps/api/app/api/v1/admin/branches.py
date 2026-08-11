"""Branch admin routes. HTTP only -- every query lives in branch_service."""

from __future__ import annotations

from fastapi import APIRouter, status
from pydantic import BaseModel

from app.api.v1.admin._shared import BranchScope, DbSession, conflict, forbidden_branch, not_found
from app.domains.branches.access import BRANCH_READ, BRANCH_WRITE, AccessSet
from app.domains.branches.schemas import (
    BranchCreate,
    BranchResponse,
    BranchSettingsUpdate,
    BranchUpdate,
    ClosureCreate,
    OpeningHourInput,
)
from app.domains.branches.service import (
    BranchNotFoundError,
    BranchSlugConflictError,
    branch_service,
)

router = APIRouter()


class OpeningHoursReplace(BaseModel):
    items: list[OpeningHourInput]


def _payload(branch) -> dict:
    return BranchResponse.model_validate(branch).model_dump(mode="json")


@router.get("/branches")
async def list_branches(session: DbSession, scope: BranchScope):
    if not scope.has(BRANCH_READ):
        return forbidden_branch()
    branches = await branch_service.list(session, branch_ids=scope.branches_with(BRANCH_READ))
    return {"items": [_payload(branch) for branch in branches]}


@router.post("/branches", status_code=status.HTTP_201_CREATED)
async def create_branch(payload: BranchCreate, session: DbSession, scope: BranchScope):
    # Creating a branch is inherently org-wide: there is no branch to be scoped to yet.
    if not scope.is_org_wide or not scope.has(BRANCH_WRITE):
        return forbidden_branch()
    try:
        branch = await branch_service.create(session, payload)
    except BranchSlugConflictError:
        return conflict("branch_slug_conflict", "A branch with this slug already exists.")
    return {"data": _payload(branch)}


@router.get("/branches/{branch_id}")
async def get_branch(branch_id: int, session: DbSession, scope: BranchScope):
    try:
        scope.assert_branch(BRANCH_READ, branch_id)
    except AccessSet.BranchForbidden:
        return forbidden_branch()
    try:
        branch = await branch_service.get(session, branch_id)
    except BranchNotFoundError:
        return not_found("branch_not_found", "Branch not found.")
    return {"data": _payload(branch)}


@router.patch("/branches/{branch_id}")
async def update_branch(
    branch_id: int, payload: BranchUpdate, session: DbSession, scope: BranchScope
):
    try:
        scope.assert_branch(BRANCH_WRITE, branch_id)
    except AccessSet.BranchForbidden:
        return forbidden_branch()
    try:
        branch = await branch_service.update(session, branch_id, payload)
    except BranchNotFoundError:
        return not_found("branch_not_found", "Branch not found.")
    except BranchSlugConflictError:
        return conflict("branch_slug_conflict", "A branch with this slug already exists.")
    return {"data": _payload(branch)}


@router.delete("/branches/{branch_id}")
async def delete_branch(branch_id: int, session: DbSession, scope: BranchScope):
    if not scope.is_org_wide or not scope.has(BRANCH_WRITE):
        return forbidden_branch()
    try:
        await branch_service.delete(session, branch_id)
    except BranchNotFoundError:
        return not_found("branch_not_found", "Branch not found.")
    return {"data": {"deleted": True}}


@router.put("/branches/{branch_id}/settings")
async def update_branch_settings(
    branch_id: int, payload: BranchSettingsUpdate, session: DbSession, scope: BranchScope
):
    try:
        scope.assert_branch(BRANCH_WRITE, branch_id)
    except AccessSet.BranchForbidden:
        return forbidden_branch()
    try:
        branch = await branch_service.update_settings(session, branch_id, payload)
    except BranchNotFoundError:
        return not_found("branch_not_found", "Branch not found.")
    return {"data": _payload(branch)}


@router.put("/branches/{branch_id}/opening-hours")
async def replace_opening_hours(
    branch_id: int, payload: OpeningHoursReplace, session: DbSession, scope: BranchScope
):
    try:
        scope.assert_branch(BRANCH_WRITE, branch_id)
    except AccessSet.BranchForbidden:
        return forbidden_branch()
    try:
        branch = await branch_service.replace_opening_hours(session, branch_id, payload.items)
    except BranchNotFoundError:
        return not_found("branch_not_found", "Branch not found.")
    return {"data": _payload(branch)}


@router.post("/branches/{branch_id}/closures", status_code=status.HTTP_201_CREATED)
async def add_closure(
    branch_id: int, payload: ClosureCreate, session: DbSession, scope: BranchScope
):
    try:
        scope.assert_branch(BRANCH_WRITE, branch_id)
    except AccessSet.BranchForbidden:
        return forbidden_branch()
    try:
        await branch_service.add_closure(session, branch_id, payload)
        branch = await branch_service.get(session, branch_id)
    except BranchNotFoundError:
        return not_found("branch_not_found", "Branch not found.")
    return {"data": _payload(branch)}


@router.delete("/branches/{branch_id}/closures/{closure_id}")
async def delete_closure(branch_id: int, closure_id: int, session: DbSession, scope: BranchScope):
    try:
        scope.assert_branch(BRANCH_WRITE, branch_id)
    except AccessSet.BranchForbidden:
        return forbidden_branch()
    try:
        await branch_service.delete_closure(session, branch_id, closure_id)
    except BranchNotFoundError:
        return not_found("closure_not_found", "Closure not found.")
    return {"data": {"deleted": True}}
