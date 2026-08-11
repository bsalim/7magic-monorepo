from __future__ import annotations

import os
import subprocess
from pathlib import Path

API_ROOT = Path(__file__).resolve().parents[1]


def test_migrations_run_on_a_fresh_sqlite_database(tmp_path) -> None:
    """Guards the SQLite-compatibility rules: JSONB, ARRAY or a bare ALTER on
    user_roles all fail here rather than in production."""
    database = tmp_path / "migration-test.db"
    result = subprocess.run(
        ["uv", "run", "alembic", "upgrade", "head"],
        cwd=API_ROOT,
        env={**os.environ, "DATABASE_URL": f"sqlite+aiosqlite:///{database}"},
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert database.exists()
