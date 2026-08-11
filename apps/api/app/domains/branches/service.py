from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.branches.models import Branch, BranchClosure, BranchOpeningHour, BranchSettings
from app.domains.branches.schemas import (
    BranchCreate,
    BranchSettingsUpdate,
    BranchUpdate,
    ClosureCreate,
    OpeningHourInput,
)


class BranchNotFoundError(Exception):
    pass


class BranchSlugConflictError(Exception):
    pass


class BranchService:
    async def list(
        self,
        session: AsyncSession,
        *,
        branch_ids: list[int] | None = None,
        active_only: bool = False,
    ) -> list[Branch]:
        """`branch_ids=None` means "every branch" and is only ever passed by an
        org-wide caller; the router resolves the scope, never this method."""
        query = select(Branch).where(Branch.deleted_at.is_(None)).order_by(Branch.name)
        if branch_ids is not None:
            query = query.where(Branch.id.in_(branch_ids))
        if active_only:
            query = query.where(Branch.active.is_(True))
        return list((await session.scalars(query)).all())

    async def get(self, session: AsyncSession, branch_id: int) -> Branch:
        branch = await session.scalar(
            select(Branch).where(Branch.id == branch_id, Branch.deleted_at.is_(None))
        )
        if branch is None:
            raise BranchNotFoundError
        return branch

    async def get_by_slug(self, session: AsyncSession, slug: str) -> Branch:
        branch = await session.scalar(
            select(Branch).where(Branch.slug == slug, Branch.deleted_at.is_(None))
        )
        if branch is None:
            raise BranchNotFoundError
        return branch

    async def create(self, session: AsyncSession, payload: BranchCreate) -> Branch:
        await self._assert_slug_free(session, payload.slug, exclude_id=None)

        data = payload.model_dump()
        make_default = data.pop("is_default")
        branch = Branch(**data)
        branch.settings = BranchSettings(tour_notification_recipients=[])

        # The first branch is the default whether or not the caller asked: /tour
        # with no slug must always land somewhere.
        existing = await session.scalar(select(Branch.id).where(Branch.deleted_at.is_(None)))
        branch.is_default = make_default or existing is None

        session.add(branch)
        await session.flush()
        if branch.is_default:
            await self._demote_other_defaults(session, keep_id=branch.id)
        await session.commit()
        await session.refresh(branch)
        return branch

    async def update(self, session: AsyncSession, branch_id: int, payload: BranchUpdate) -> Branch:
        branch = await self.get(session, branch_id)
        changes = payload.model_dump(exclude_unset=True)

        if "slug" in changes and changes["slug"] != branch.slug:
            await self._assert_slug_free(session, changes["slug"], exclude_id=branch.id)

        promote = changes.pop("is_default", None)
        for key, value in changes.items():
            setattr(branch, key, value)

        if promote is True:
            branch.is_default = True
            await self._demote_other_defaults(session, keep_id=branch.id)
        elif promote is False and branch.is_default:
            # Refuse to leave the business with no default branch.
            branch.is_default = False
            fallback = await session.scalar(
                select(Branch)
                .where(Branch.id != branch.id, Branch.deleted_at.is_(None))
                .order_by(Branch.id)
            )
            if fallback is not None:
                fallback.is_default = True
            else:
                branch.is_default = True

        await session.commit()
        await session.refresh(branch)
        return branch

    async def delete(self, session: AsyncSession, branch_id: int) -> None:
        branch = await self.get(session, branch_id)
        branch.deleted_at = datetime.now(UTC)
        if branch.is_default:
            branch.is_default = False
            fallback = await session.scalar(
                select(Branch)
                .where(Branch.id != branch.id, Branch.deleted_at.is_(None))
                .order_by(Branch.id)
            )
            if fallback is not None:
                fallback.is_default = True
        await session.commit()

    async def update_settings(
        self, session: AsyncSession, branch_id: int, payload: BranchSettingsUpdate
    ) -> Branch:
        branch = await self.get(session, branch_id)
        if branch.settings is None:
            branch.settings = BranchSettings(tour_notification_recipients=[])
            await session.flush()
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(branch.settings, key, value)
        await session.commit()
        await session.refresh(branch)
        return branch

    async def replace_opening_hours(
        self, session: AsyncSession, branch_id: int, rows: list[OpeningHourInput]
    ) -> Branch:
        """Whole-week replace. A per-row PATCH invites the half-saved week the
        source platform kept producing when a day was dropped from the form."""
        branch = await self.get(session, branch_id)
        branch.opening_hours.clear()
        await session.flush()
        for row in rows:
            branch.opening_hours.append(BranchOpeningHour(**row.model_dump()))
        await session.commit()
        await session.refresh(branch)
        return branch

    async def add_closure(
        self, session: AsyncSession, branch_id: int, payload: ClosureCreate
    ) -> BranchClosure:
        branch = await self.get(session, branch_id)
        closure = BranchClosure(**payload.model_dump())
        branch.closures.append(closure)
        await session.commit()
        await session.refresh(closure)
        return closure

    async def delete_closure(self, session: AsyncSession, branch_id: int, closure_id: int) -> None:
        closure = await session.scalar(
            select(BranchClosure).where(
                BranchClosure.id == closure_id, BranchClosure.branch_id == branch_id
            )
        )
        if closure is None:
            raise BranchNotFoundError
        await session.delete(closure)
        await session.commit()

    async def _assert_slug_free(
        self, session: AsyncSession, slug: str, *, exclude_id: int | None
    ) -> None:
        query = select(Branch.id).where(Branch.slug == slug, Branch.deleted_at.is_(None))
        if exclude_id is not None:
            query = query.where(Branch.id != exclude_id)
        if await session.scalar(query) is not None:
            raise BranchSlugConflictError

    async def _demote_other_defaults(self, session: AsyncSession, *, keep_id: int) -> None:
        """SQLite has no partial unique index, so the invariant lives here. It runs
        inside the caller's transaction, so no window exists with two defaults."""
        await session.execute(update(Branch).where(Branch.id != keep_id).values(is_default=False))


branch_service = BranchService()
