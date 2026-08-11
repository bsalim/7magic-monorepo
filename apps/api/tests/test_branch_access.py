from __future__ import annotations

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app import models  # noqa: F401
from app.core.database import Base
from app.core.security import hash_password
from app.domains.branches.access import (
    BRANCH_WRITE,
    EVENT_WRITE,
    REGISTRATION_WRITE,
    AccessSet,
    access_set_for,
)
from app.domains.branches.models import Branch
from app.models import Role, User, UserRole
from app.services.auth import resolve_admin_user_by_id


def test_org_wide_role_grants_every_branch() -> None:
    access = access_set_for([("admin", None)])

    assert access.is_org_wide is True
    assert access.has(EVENT_WRITE) is True
    assert access.has(EVENT_WRITE, branch_id=42) is True
    assert access.branches_with(EVENT_WRITE) is None  # None == unbounded


def test_branch_scoped_role_grants_only_its_branch() -> None:
    access = access_set_for([("branch_manager", 7)])

    assert access.is_org_wide is False
    assert access.has(EVENT_WRITE, branch_id=7) is True
    assert access.has(EVENT_WRITE, branch_id=8) is False
    assert access.branches_with(EVENT_WRITE) == [7]


def test_branch_staff_may_manage_registrations_but_not_branch_settings() -> None:
    access = access_set_for([("branch_staff", 7)])

    assert access.has(REGISTRATION_WRITE, branch_id=7) is True
    assert access.has(BRANCH_WRITE, branch_id=7) is False


def test_grants_from_several_branches_accumulate() -> None:
    access = access_set_for([("branch_manager", 7), ("branch_staff", 9)])

    assert sorted(access.branches_with(REGISTRATION_WRITE) or []) == [7, 9]
    assert access.branches_with(BRANCH_WRITE) == [7]


def test_an_unknown_role_grants_nothing() -> None:
    access = access_set_for([("editor", None)])

    assert access.has(EVENT_WRITE) is False
    assert access.branches_with(EVENT_WRITE) == []


def test_permitted_or_raise_rejects_a_branch_outside_the_scope() -> None:
    access = access_set_for([("branch_manager", 7)])

    assert access.assert_branch(EVENT_WRITE, 7) is None
    with pytest.raises(AccessSet.BranchForbidden):
        access.assert_branch(EVENT_WRITE, 8)


@pytest_asyncio.fixture()
async def auth_session(tmp_path):
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'access.db'}")
    factory = async_sessionmaker(engine, autoflush=False, expire_on_commit=False)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    try:
        async with factory() as db:
            yield db
    finally:
        await engine.dispose()


@pytest.mark.asyncio
async def test_a_branch_manager_may_sign_in_and_carries_its_branch(auth_session) -> None:
    branch = Branch(slug="bali", name="7Magic Bali", timezone="Asia/Makassar")
    role = Role(name="branch_manager")
    user = User(email="manager@7magic.test", password_hash=hash_password("secret-password"))
    auth_session.add_all([branch, role, user])
    await auth_session.flush()
    auth_session.add(UserRole(user_id=user.id, role_id=role.id, branch_id=branch.id))
    await auth_session.commit()

    authenticated = await resolve_admin_user_by_id(auth_session, user_id=user.id)

    assert authenticated.branch_grants == (("branch_manager", branch.id),)
    assert access_set_for(authenticated.branch_grants).branches_with(EVENT_WRITE) == [branch.id]
