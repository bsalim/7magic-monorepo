"""Admin showcase CRUD, focused on what the CMS list and edit form rely on.

The CMS edit form posts every field back on save, so anything the detail
endpoint withholds gets written back as null. image_variants was withheld,
which meant a title fix silently cost the showcase its responsive srcset.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator, Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.api.v1.dependencies import require_admin_user
from app.core.database import Base, get_db_session
from app.main import app
from app.models import User
from app.services.auth import AuthenticatedUser

VARIANTS = {
    "original": "https://cdn.test/showcases/abc.jpg",
    "webp_srcset": "https://cdn.test/showcases/abc-320.webp 320w, https://cdn.test/showcases/abc-640.webp 640w",
    "jpeg_srcset": "https://cdn.test/showcases/abc-320.jpg 320w, https://cdn.test/showcases/abc-640.jpg 640w",
    "sizes": "(max-width: 640px) 100vw, 640px",
}


@pytest.fixture()
def showcase_client(tmp_path) -> Generator[TestClient, None, None]:
    database_url = f"sqlite+aiosqlite:///{tmp_path / 'showcase-admin.db'}"
    engine = create_async_engine(database_url)
    session_factory = async_sessionmaker(engine, autoflush=False, expire_on_commit=False)

    async def override_db_session() -> AsyncGenerator[AsyncSession, None]:
        async with session_factory() as session:
            yield session

    def override_admin_user() -> AuthenticatedUser:
        return AuthenticatedUser(
            id=1,
            email="editor@7magic.test",
            username="editor",
            first_name="Editorial",
            last_name="Team",
            roles=["admin"],
        )

    async def prepare() -> None:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
        async with session_factory() as session:
            session.add(
                User(
                    id=1,
                    email="editor@7magic.test",
                    username="editor",
                    first_name="Editorial",
                    last_name="Team",
                    password_hash="",
                    active=True,
                )
            )
            await session.commit()

    import asyncio

    asyncio.run(prepare())
    previous = app.dependency_overrides.copy()
    app.dependency_overrides[get_db_session] = override_db_session
    app.dependency_overrides[require_admin_user] = override_admin_user
    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous)
        asyncio.run(engine.dispose())


def _payload(**overrides) -> dict:
    body = {
        "title_id": "Pernikahan Dina & Rangga",
        "slug": "pernikahan-dina-rangga",
        "body_id": "Resepsi di Jakarta Selatan.",
        "showcase_date": "2026-05-17",
        "status": "draft",
        "image_url": "https://cdn.test/showcases/abc.jpg",
        "image_storage_key": "showcases/abc.jpg",
        "image_variants": VARIANTS,
    }
    body.update(overrides)
    return body


def test_detail_returns_the_stored_image_variants(showcase_client: TestClient) -> None:
    """Without this the CMS form has nothing to post back on save."""
    created = showcase_client.post("/api/v1/admin/showcases", json=_payload()).json()

    detail = showcase_client.get(f"/api/v1/admin/showcases/{created['id']}")

    assert detail.status_code == 200
    assert detail.json()["image_variants"] == VARIANTS


def test_a_showcase_without_variants_reports_none(showcase_client: TestClient) -> None:
    created = showcase_client.post(
        "/api/v1/admin/showcases", json=_payload(image_variants=None)
    ).json()

    assert created["image_variants"] is None


def test_editing_text_keeps_the_variants_when_they_are_posted_back(
    showcase_client: TestClient,
) -> None:
    """The round-trip the CMS edit page performs: read detail, post it all back."""
    created = showcase_client.post("/api/v1/admin/showcases", json=_payload()).json()
    detail = showcase_client.get(f"/api/v1/admin/showcases/{created['id']}").json()

    updated = showcase_client.patch(
        f"/api/v1/admin/showcases/{created['id']}",
        json={
            "title_id": "Pernikahan Dina dan Rangga",
            "image_url": detail["image_url"],
            "image_storage_key": detail["image_storage_key"],
            "image_variants": detail["image_variants"],
        },
    )

    assert updated.status_code == 200
    assert updated.json()["title_id"] == "Pernikahan Dina dan Rangga"
    assert updated.json()["image_variants"] == VARIANTS

    # And the public card still carries the srcset, which is the point.
    showcase_client.patch(
        f"/api/v1/admin/showcases/{created['id']}", json={"status": "published"}
    )
    card = showcase_client.get("/api/v1/public/showcases").json()["items"][0]
    assert card["image"]["webp_srcset"] == VARIANTS["webp_srcset"]
    assert card["image"]["sizes"] == VARIANTS["sizes"]


def test_status_only_patch_leaves_every_other_field_alone(
    showcase_client: TestClient,
) -> None:
    """What the list page's Publish shortcut sends -- it knows nothing else."""
    created = showcase_client.post("/api/v1/admin/showcases", json=_payload()).json()

    published = showcase_client.patch(
        f"/api/v1/admin/showcases/{created['id']}", json={"status": "published"}
    )

    assert published.status_code == 200
    body = published.json()
    assert body["status"] == "published"
    assert body["title_id"] == "Pernikahan Dina & Rangga"
    assert body["body_id"] == "Resepsi di Jakarta Selatan."
    assert body["showcase_date"] == "2026-05-17"
    assert body["image_url"] == "https://cdn.test/showcases/abc.jpg"
    assert body["image_variants"] == VARIANTS


def test_unpublishing_hides_it_from_the_public_list(showcase_client: TestClient) -> None:
    created = showcase_client.post(
        "/api/v1/admin/showcases", json=_payload(status="published")
    ).json()
    assert showcase_client.get("/api/v1/public/showcases").json()["total"] == 1

    showcase_client.patch(
        f"/api/v1/admin/showcases/{created['id']}", json={"status": "draft"}
    )

    assert showcase_client.get("/api/v1/public/showcases").json()["total"] == 0
    # Still listed for the editor, which is how they find it again.
    assert len(showcase_client.get("/api/v1/admin/showcases").json()["items"]) == 1


def test_an_archived_showcase_can_be_published_directly(
    showcase_client: TestClient,
) -> None:
    """The list shortcut offers Publish on archived rows, not just drafts."""
    created = showcase_client.post(
        "/api/v1/admin/showcases", json=_payload(status="archived")
    ).json()

    published = showcase_client.patch(
        f"/api/v1/admin/showcases/{created['id']}", json={"status": "published"}
    )

    assert published.status_code == 200
    assert published.json()["status"] == "published"


def test_unknown_showcase_returns_404(showcase_client: TestClient) -> None:
    assert showcase_client.get("/api/v1/admin/showcases/999999").status_code == 404
