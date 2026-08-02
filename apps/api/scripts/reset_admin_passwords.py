"""Pre-launch utility: reset every admin password to Admin123 and revoke sessions.

Do not run after launch.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import delete, select

from app.core.database import AsyncSessionLocal
from app.core.security import hash_password
from app.models import Role, User, UserRole, UserSession

NEW_PASSWORD = "Admin123"


async def main() -> None:
    async with AsyncSessionLocal() as session:
        admins = (
            (
                await session.execute(
                    select(User)
                    .join(UserRole, UserRole.user_id == User.id)
                    .join(Role, Role.id == UserRole.role_id)
                    .where(Role.name == "admin")
                )
            )
            .scalars()
            .unique()
            .all()
        )
        for user in admins:
            user.password_hash = hash_password(NEW_PASSWORD)
        await session.execute(delete(UserSession))
        await session.commit()

    emails = ", ".join(user.email for user in admins) or "<none>"
    print(f"Reset {len(admins)} admin password(s) to {NEW_PASSWORD!r}: {emails}")
    print("All sessions revoked.")


if __name__ == "__main__":
    asyncio.run(main())
