"""Admin article CRUD.

Article writes used to go through catalog_service, which appended to an
in-memory list -- articles created through the CMS never reached the database
and vanished on restart. These tests pin the DB-backed behaviour.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator, Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.api.v1.dependencies import require_admin_user
from app.core.database import Base, get_db_session
from app.main import app
from app.models import ArticleCategory, User
from app.services.auth import AuthenticatedUser


@pytest.fixture()
def article_client(tmp_path) -> Generator[TestClient, None, None]:
    database_url = f"sqlite+aiosqlite:///{tmp_path / 'article-admin.db'}"
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
            session.add(
                ArticleCategory(category="Wedding Venue", category_slug="wedding-venue")
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
        "title_id": "Panduan Venue Jakarta",
        "slug": "panduan-venue-jakarta",
        "summary_id": "Ringkasan panduan memilih venue.",
        "body_id": "<h2>Judul</h2><p>Isi artikel tentang venue pernikahan.</p>",
        "category": "wedding-venue",
        "topic": ["venue"],
        "status": "draft",
    }
    body.update(overrides)
    return body


def test_create_article_persists_to_the_database(article_client: TestClient) -> None:
    response = article_client.post("/api/v1/admin/articles", json=_payload())
    assert response.status_code == 201
    created = response.json()

    # It must be readable back, which an in-memory list would not survive.
    detail = article_client.get(f"/api/v1/admin/articles/{created['id']}")
    assert detail.status_code == 200
    assert detail.json()["slug"] == "panduan-venue-jakarta"


def test_english_is_optional_and_absent_by_default(article_client: TestClient) -> None:
    created = article_client.post("/api/v1/admin/articles", json=_payload()).json()

    assert created["title_id"] == "Panduan Venue Jakarta"
    assert created["title_en"] == ""
    assert created["has_english"] is False


def test_word_count_and_plain_text_are_derived_from_the_indonesian_body(
    article_client: TestClient,
) -> None:
    """Editors submit rich text; the search-facing fields track the canonical
    Indonesian body rather than being asked for."""
    created = article_client.post(
        "/api/v1/admin/articles",
        json=_payload(body_id="<p>One two three</p><p>four five</p>"),
    ).json()

    assert created["word_count"] == 5


def test_duplicate_slug_in_the_same_category_is_rejected(
    article_client: TestClient,
) -> None:
    article_client.post("/api/v1/admin/articles", json=_payload())
    duplicate = article_client.post("/api/v1/admin/articles", json=_payload())

    assert duplicate.status_code == 409
    assert duplicate.json()["error"]["code"] == "slug_conflict"


def test_english_text_lives_on_the_same_row(article_client: TestClient) -> None:
    created = article_client.post(
        "/api/v1/admin/articles",
        json=_payload(title_en="Jakarta Venue Guide", body_en="<p>English body.</p>"),
    ).json()

    assert created["title_en"] == "Jakarta Venue Guide"
    assert created["has_english"] is True
    # Same row, so one id and one slug serve both languages.
    assert created["slug"] == "panduan-venue-jakarta"


def test_blank_english_clears_rather_than_publishing_an_empty_translation(
    article_client: TestClient,
) -> None:
    created = article_client.post(
        "/api/v1/admin/articles",
        json=_payload(title_en="Jakarta Venue Guide", body_en="<p>English body.</p>"),
    ).json()

    cleared = article_client.patch(
        f"/api/v1/admin/articles/{created['id']}",
        json={"title_en": "   ", "body_en": ""},
    ).json()

    assert cleared["title_en"] == ""
    assert cleared["has_english"] is False


def test_update_changes_content_and_recomputes_word_count(
    article_client: TestClient,
) -> None:
    created = article_client.post("/api/v1/admin/articles", json=_payload()).json()

    updated = article_client.patch(
        f"/api/v1/admin/articles/{created['id']}",
        json={"title_id": "Judul Baru", "body_id": "<p>satu dua tiga empat</p>"},
    )

    assert updated.status_code == 200
    assert updated.json()["title_id"] == "Judul Baru"
    assert updated.json()["word_count"] == 4


def test_publishing_sets_published_at(article_client: TestClient) -> None:
    created = article_client.post("/api/v1/admin/articles", json=_payload()).json()
    assert created["published_at"] is None

    published = article_client.patch(
        f"/api/v1/admin/articles/{created['id']}", json={"status": "published"}
    )

    assert published.status_code == 200
    assert published.json()["status"] == "published"
    assert published.json()["published_at"]


def test_admin_list_shows_drafts_but_public_listing_does_not(
    article_client: TestClient,
) -> None:
    article_client.post("/api/v1/admin/articles", json=_payload())

    admin = article_client.get("/api/v1/admin/articles").json()
    assert [item["slug"] for item in admin["items"]] == ["panduan-venue-jakarta"]

    public = article_client.get("/api/v1/public/articles").json()
    assert public["items"] == []


def test_trashed_article_disappears_from_the_admin_list(
    article_client: TestClient,
) -> None:
    created = article_client.post("/api/v1/admin/articles", json=_payload()).json()

    deleted = article_client.delete(f"/api/v1/admin/articles/{created['id']}")
    assert deleted.status_code == 200

    admin = article_client.get("/api/v1/admin/articles").json()
    assert admin["items"] == []


def test_unknown_article_returns_404(article_client: TestClient) -> None:
    assert article_client.get("/api/v1/admin/articles/999999").status_code == 404




def test_dashboard_counts_come_from_the_database(article_client: TestClient) -> None:
    """The dashboard read article and lead totals from in-memory fixtures, so it
    showed numbers unrelated to the real content."""
    article_client.post("/api/v1/admin/articles", json=_payload())
    article_client.post(
        "/api/v1/admin/articles",
        json=_payload(title_id="Published One", slug="published-one", status="published"),
    )

    totals = article_client.get("/api/v1/admin/dashboard").json()["totals"]

    assert totals["articles"] == 2
    assert totals["drafts"] == 1
    # No leads have been submitted in this fixture, so it cannot be the old 18.
    assert totals["leads"] == 0
