from __future__ import annotations

import argparse
import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.database import AsyncSessionLocal
from app.services.user_seed import seed_admin_user


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Seed an active CMS admin user.")
    parser.add_argument("--email", default=os.getenv("ADMIN_EMAIL"))
    parser.add_argument("--password", default=os.getenv("ADMIN_PASSWORD"))
    return parser.parse_args()


async def main() -> None:
    args = parse_args()
    if not args.email:
        raise SystemExit("Missing --email or ADMIN_EMAIL")
    if not args.password:
        raise SystemExit("Missing --password or ADMIN_PASSWORD")

    async with AsyncSessionLocal() as session:
        user = await seed_admin_user(session, email=args.email, password=args.password)

    print(f"Seeded admin user: {user.email}")


if __name__ == "__main__":
    asyncio.run(main())
