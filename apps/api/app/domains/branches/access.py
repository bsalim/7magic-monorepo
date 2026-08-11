"""Branch-scoped permissions.

A role row with `branch_id IS NULL` is org-wide; a row with a branch is scoped to
it. `branches_with` returns `None` for an org-wide grant, meaning *unbounded* --
callers must treat that as "apply no branch filter", not as "no branches".
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field

BRANCH_READ = "branch:read"
BRANCH_WRITE = "branch:write"
EVENT_READ = "event:read"
EVENT_WRITE = "event:write"
REGISTRATION_READ = "registration:read"
REGISTRATION_WRITE = "registration:write"

ALL_PERMISSIONS = frozenset(
    {BRANCH_READ, BRANCH_WRITE, EVENT_READ, EVENT_WRITE, REGISTRATION_READ, REGISTRATION_WRITE}
)

# A branch manager runs their branch outright. Branch staff work the front desk:
# they read events and handle registrations, but do not edit the branch itself.
ROLE_PERMISSIONS: dict[str, frozenset[str]] = {
    "owner": ALL_PERMISSIONS,
    "admin": ALL_PERMISSIONS,
    "branch_manager": ALL_PERMISSIONS,
    "branch_staff": frozenset({BRANCH_READ, EVENT_READ, REGISTRATION_READ, REGISTRATION_WRITE}),
}

# Roles that may sign in to the CMS at all.
CMS_ROLES = frozenset(ROLE_PERMISSIONS)


@dataclass(frozen=True)
class AccessSet:
    org_wide: frozenset[str] = frozenset()
    per_branch: dict[int, frozenset[str]] = field(default_factory=dict)

    class BranchForbidden(Exception):
        pass

    @property
    def is_org_wide(self) -> bool:
        return bool(self.org_wide)

    def has(self, permission: str, branch_id: int | None = None) -> bool:
        if permission in self.org_wide:
            return True
        if branch_id is None:
            return any(permission in perms for perms in self.per_branch.values())
        return permission in self.per_branch.get(branch_id, frozenset())

    def branches_with(self, permission: str) -> list[int] | None:
        """`None` means unbounded -- do not filter. `[]` means no access at all."""
        if permission in self.org_wide:
            return None
        return sorted(
            branch_id for branch_id, perms in self.per_branch.items() if permission in perms
        )

    def assert_branch(self, permission: str, branch_id: int | None) -> None:
        """Raises unless the caller may act on `branch_id`. `branch_id=None` means an
        all-branch record, which only an org-wide grant may touch."""
        if permission in self.org_wide:
            return
        if branch_id is None or permission not in self.per_branch.get(branch_id, frozenset()):
            raise AccessSet.BranchForbidden
        return


def access_set_for(grants: Iterable[tuple[str, int | None]]) -> AccessSet:
    org_wide: set[str] = set()
    per_branch: dict[int, set[str]] = {}
    for role_name, branch_id in grants:
        permissions = ROLE_PERMISSIONS.get(role_name)
        if not permissions:
            continue
        if branch_id is None:
            org_wide.update(permissions)
        else:
            per_branch.setdefault(branch_id, set()).update(permissions)
    return AccessSet(
        org_wide=frozenset(org_wide),
        per_branch={key: frozenset(value) for key, value in per_branch.items()},
    )
