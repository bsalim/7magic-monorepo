import asyncio
from collections.abc import AsyncGenerator, Generator
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app import models  # noqa: F401
from app.api.v1.dependencies import require_admin_user
from app.core.database import Base, get_db_session
from app.main import app
from app.models import Article, ArticleCategory, ArticleImage, User, Venue
from app.services.auth import AuthenticatedUser
from app.services.leads import lead_service


@pytest.fixture()
def admin_client(tmp_path) -> Generator[TestClient, None, None]:
    """Admin client backed by an isolated SQLite database.

    Admin venue endpoints are database-backed, so tests must not touch the
    developer's live Postgres database. Each test gets a fresh schema seeded
    with a single venue (enough for the dashboard contract).
    """
    database_url = f"sqlite+aiosqlite:///{tmp_path / 'admin-test.db'}"
    engine = create_async_engine(database_url)
    session_factory = async_sessionmaker(engine, autoflush=False, expire_on_commit=False)

    async def override_db_session() -> AsyncGenerator[AsyncSession, None]:
        async with session_factory() as session:
            yield session

    async def prepare_database() -> None:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
        async with session_factory() as session:
            session.add(
                Venue(
                    name="Seed Venue",
                    slug="seed-venue",
                    city="jakarta",
                    district="Jakarta Pusat",
                    address="Jl. Seed No.1",
                    stars=5,
                    description="Seed venue for admin contract tests.",
                    price_for_total_pax=250,
                    status="active",
                )
            )
            await session.commit()

    asyncio.run(prepare_database())

    previous_overrides = app.dependency_overrides.copy()
    app.dependency_overrides[get_db_session] = override_db_session
    app.dependency_overrides[require_admin_user] = lambda: AuthenticatedUser(
        id=1,
        email="byonosalim@gmail.com",
        username="byonosalim",
        first_name="Admin",
        last_name="User",
        roles=["admin"],
    )

    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous_overrides)
        asyncio.run(engine.dispose())


@pytest.fixture()
def public_article_client(tmp_path) -> Generator[TestClient, None, None]:
    database_url = f"sqlite+aiosqlite:///{tmp_path / 'public-articles-test.db'}"
    engine = create_async_engine(database_url)
    session_factory = async_sessionmaker(engine, autoflush=False, expire_on_commit=False)

    async def override_db_session() -> AsyncGenerator[AsyncSession, None]:
        async with session_factory() as session:
            yield session

    async def prepare_database() -> None:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
        async with session_factory() as session:
            author = User(
                email="editorial@7magic.test",
                username="7magic-editorial",
                first_name="7Magic",
                last_name="Editorial",
                password_hash="",
                active=True,
            )
            category = ArticleCategory(category="Wedding Venue", category_slug="wedding-venue")
            published = Article(
                author=author,
                category=category,
                title_id="Database Wedding Venue Guide",
                slug="database-wedding-venue-guide",
                summary_id="A published article seeded in the articles table.",
                body_id="<h2>DB Article</h2><p>Real article table content.</p>",
                content_text="DB Article Real article table content.",
                word_count=6,
                featured=True,
                published_at=datetime(2026, 6, 1, tzinfo=timezone.utc),
                status="published",
                trash=False,
                topic=["packages"],
            )
            published.images.append(
                ArticleImage(
                    filename="db-article.jpg",
                    file_type="jpg",
                    image="articles/db-article.jpg",
                    cdn_url="https://cdn.7magic.test/articles/db-article.jpg",
                )
            )
            draft = Article(
                author=author,
                category=category,
                title_id="Draft Article",
                slug="draft-article",
                summary_id="This draft must not be public.",
                body_id="<p>Draft</p>",
                content_text="Draft",
                word_count=1,
                featured=False,
                status="draft",
                trash=False,
                topic=["packages"],
            )
            session.add_all([published, draft])
            await session.commit()

    asyncio.run(prepare_database())

    previous_overrides = app.dependency_overrides.copy()
    app.dependency_overrides[get_db_session] = override_db_session

    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous_overrides)
        asyncio.run(engine.dispose())


def test_public_home_contract() -> None:
    client = TestClient(app)
    response = client.get("/api/v1/public/home")

    assert response.status_code == 200
    payload = response.json()
    assert payload["hero"]["title"]
    assert payload["featured_venues"]
    assert payload["testimonials"]


def test_public_venue_search_contract() -> None:
    client = TestClient(app)
    response = client.get("/api/v1/public/venues", params={"city": "jakarta", "stars_min": 5})

    assert response.status_code == 200
    payload = response.json()
    assert payload["pagination"]["total"] >= 1
    assert all(item["city"] == "jakarta" for item in payload["items"])


def test_public_article_rollup_routes_filter_published_articles(public_article_client: TestClient) -> None:
    client = public_article_client

    by_category = client.get("/api/v1/public/articles/categories/wedding-venue")
    by_topic = client.get("/api/v1/public/articles/topics/packages")
    by_author = client.get("/api/v1/public/articles/authors/7magic-editorial")

    assert by_category.status_code == 200
    assert by_topic.status_code == 200
    assert by_author.status_code == 200

    category_payload = by_category.json()
    topic_payload = by_topic.json()
    author_payload = by_author.json()
    assert category_payload["items"]
    assert topic_payload["items"]
    assert author_payload["items"]
    assert all(item["category"] == "wedding-venue" for item in category_payload["items"])
    assert all(item["status"] == "published" for item in topic_payload["items"])
    assert all(item["author"] == "7Magic Editorial" for item in author_payload["items"])


def test_public_articles_use_database_records(public_article_client: TestClient) -> None:
    response = public_article_client.get("/api/v1/public/articles")

    assert response.status_code == 200
    payload = response.json()
    assert payload["pagination"]["total"] == 1
    assert payload["items"][0]["title"] == "Database Wedding Venue Guide"
    assert payload["items"][0]["image_url"] == "https://cdn.7magic.test/articles/db-article.jpg"


def test_public_article_detail_uses_database_record(public_article_client: TestClient) -> None:
    response = public_article_client.get(
        "/api/v1/public/articles/wedding-venue/database-wedding-venue-guide"
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["title"] == "Database Wedding Venue Guide"
    assert payload["content"] == "<h2>DB Article</h2><p>Real article table content.</p>"
    assert payload["topic"] == ["packages"]


def test_public_contact_lead_contract(public_article_client: TestClient) -> None:
    """Leads must reach the database. They previously went to an in-memory list
    and were lost whenever the API restarted."""
    response = public_article_client.post(
        "/api/v1/public/contact-leads",
        json={
            "name": "Ayu Santoso",
            "email": "ayu@example.com",
            "phone": "+628123456789",
            "message": "Please send Jakarta ballroom package options.",
            "source_path": "/contact",
            "venue_slug": "kempinski-indonesia",
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["id"] >= 1
    assert payload["status"] == "received"
    assert payload["message"] == "Lead received."
    # A real row, not a counter: the id must come back from the table.
    assert payload["created_at"]


def test_venue_pricing_request_is_persisted(public_article_client: TestClient) -> None:
    """Venue prices are hidden, so this modal is the only route to them. The
    form used to discard submissions entirely."""
    response = public_article_client.post(
        "/api/v1/public/venue-pricing-requests",
        json={
            "name": "Budi Hartono",
            "whatsapp": "+628999888777",
            "email": "budi@example.com",
            "wedding_date": "2027-05-20",
            "best_time_to_reach": "afternoon",
            "venue_name": "The Ritz-Carlton Jakarta",
            "venue_slug": "ritz-carlton-jakarta",
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["status"] == "received"
    assert payload["id"] >= 1


class RecordingWhatsApp:
    """Stands in for the Bird notifier so the wiring can be asserted without a
    live send."""

    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    async def send_lead_alert(self, **kwargs: object) -> bool:
        self.calls.append(kwargs)
        return True


def test_contact_form_alerts_the_team_over_whatsapp(
    public_article_client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The /contact form is one of the two paths the team is alerted from."""
    recorder = RecordingWhatsApp()
    monkeypatch.setattr(lead_service, "_whatsapp", recorder)

    response = public_article_client.post(
        "/api/v1/public/contact-leads",
        json={
            "name": "Ayu Santoso",
            "email": "ayu@example.com",
            "phone": "+628123456789",
            "message": "Mau tanya paket ballroom.",
            "source_path": "/contact",
            "venue_slug": "kempinski-indonesia",
        },
    )

    assert response.status_code == 201
    assert len(recorder.calls) == 1
    call = recorder.calls[0]
    assert call["name"] == "Ayu Santoso"
    # One slot has to carry both ways of reaching them.
    assert call["contact"] == "+628123456789 / ayu@example.com"
    assert call["page"] == "kempinski-indonesia"
    assert call["message"] == "Mau tanya paket ballroom."


def test_venue_pricing_request_alerts_the_team_over_whatsapp(
    public_article_client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The venue detail modal is the other path, and the one that matters most --
    prices are not public, so this is the only way a couple can ask for them."""
    recorder = RecordingWhatsApp()
    monkeypatch.setattr(lead_service, "_whatsapp", recorder)

    response = public_article_client.post(
        "/api/v1/public/venue-pricing-requests",
        json={
            "name": "Budi Hartono",
            "whatsapp": "+628999888777",
            "email": "budi@example.com",
            "wedding_date": "2027-05-20",
            "best_time_to_reach": "afternoon",
            "venue_name": "The Ritz-Carlton Jakarta",
            "venue_slug": "ritz-carlton-jakarta",
        },
    )

    assert response.status_code == 201
    assert len(recorder.calls) == 1
    call = recorder.calls[0]
    assert call["name"] == "Budi Hartono"
    assert call["contact"] == "+628999888777 / budi@example.com"
    # The venue is the subject of this lead, so it takes the page slot.
    assert call["page"] == "The Ritz-Carlton Jakarta"
    assert call["message"] == (
        "Tanggal nikah: 2027-05-20 / Waktu dihubungi: afternoon"
    )


def test_venue_pricing_request_rejects_missing_whatsapp(
    public_article_client: TestClient,
) -> None:
    response = public_article_client.post(
        "/api/v1/public/venue-pricing-requests",
        json={"name": "No Contact"},
    )

    assert response.status_code == 422


def test_admin_dashboard_contract(admin_client: TestClient) -> None:
    client = admin_client
    response = client.get("/api/v1/admin/dashboard")

    assert response.status_code == 200
    payload = response.json()
    assert payload["totals"]["venues"] >= 1
    assert payload["recent_activity"]


def test_public_missing_venue_uses_error_envelope() -> None:
    client = TestClient(app)
    response = client.get("/api/v1/public/venues/jakarta/not-a-real-venue")

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "not_found",
            "message": "Venue not found.",
            "details": {"resource": "venue"},
        }
    }


def test_admin_routes_require_auth() -> None:
    client = TestClient(app)
    response = client.get("/api/v1/admin/dashboard")

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "missing_token"


def test_admin_can_create_article_and_reject_duplicate_slug(admin_client: TestClient) -> None:
    client = admin_client
    payload = {
        "title_id": "API First Wedding Article",
        "slug": "api-first-wedding-article",
        "summary_id": "A contract-first article created through the CMS API.",
        "body_id": "<h2 id=\"api\">API</h2><p>Write the API first.</p>",
        "category": "wedding-planning",
        "topic": ["api", "migration"],
        "status": "draft",
        "featured": False,
        "image_url": "/img/wedding-venue-deal-768.jpg",
    }

    response = client.post("/api/v1/admin/articles", json=payload)

    assert response.status_code == 201
    created = response.json()
    assert created["id"]
    assert created["slug"] == "api-first-wedding-article"
    assert created["word_count"] == 5

    duplicate = client.post("/api/v1/admin/articles", json=payload)

    assert duplicate.status_code == 409
    assert duplicate.json()["error"]["code"] == "slug_conflict"


def test_admin_can_create_venue_and_reject_duplicate_city_slug(admin_client: TestClient) -> None:
    client = admin_client
    payload = {
        "name": "API First Ballroom",
        "slug": "api-first-ballroom",
        "city": "jakarta",
        "district": "Jakarta Barat",
        "address": "Jl. API First No.1",
        "stars": 5,
        "description": "A test venue created through the API-first migration contract.",
        "price_start_from": 99000000,
        "price_for_total_pax": 250,
        "status": "active",
    }

    response = client.post("/api/v1/admin/venues", json=payload)

    assert response.status_code == 201
    created = response.json()
    assert created["path_url"] == "/wedding-venue/jakarta/api-first-ballroom"

    duplicate = client.post("/api/v1/admin/venues", json=payload)

    assert duplicate.status_code == 409
    assert duplicate.json()["error"]["code"] == "slug_conflict"


def test_admin_can_load_and_update_venue_detail(admin_client: TestClient) -> None:
    client = admin_client
    create_payload = {
        "name": "Editable Venue",
        "slug": "editable-venue",
        "city": "jakarta",
        "district": "Jakarta Pusat",
        "address": "Jl. Editable No.1",
        "stars": 4,
        "description": "A venue that can be managed from the CMS.",
        "price_start_from": 88000000,
        "price_for_total_pax": 220,
        "status": "draft",
    }
    created = client.post("/api/v1/admin/venues", json=create_payload).json()

    detail_response = client.get(f"/api/v1/admin/venues/{created['id']}")

    assert detail_response.status_code == 200
    detail = detail_response.json()
    assert detail["name"] == "Editable Venue"
    assert detail["address"] == "Jl. Editable No.1"
    assert detail["gallery"] == []

    update_response = client.patch(
        f"/api/v1/admin/venues/{created['id']}",
        json={
            "name": "Editable Venue Updated",
            "slug": "editable-venue-updated",
            "city": "jakarta",
            "district": "Jakarta Selatan",
            "address": "Jl. Editable Updated No.2",
            "stars": 5,
            "description": "Updated venue copy from the CMS.",
            "price_start_from": 118000000,
            "price_for_total_pax": 280,
            "status": "active",
        },
    )

    assert update_response.status_code == 200
    updated = update_response.json()
    assert updated["name"] == "Editable Venue Updated"
    assert updated["path_url"] == "/wedding-venue/jakarta/editable-venue-updated"
    assert updated["status"] == "active"


def test_admin_update_venue_rejects_duplicate_city_slug(admin_client: TestClient) -> None:
    client = admin_client
    first_payload = {
        "name": "First Duplicate Venue",
        "slug": "first-duplicate-venue",
        "city": "jakarta",
        "district": "Jakarta Pusat",
        "address": "Jl. First No.1",
        "stars": 5,
        "description": "The first venue in a duplicate slug check.",
        "price_start_from": 100000000,
        "price_for_total_pax": 250,
        "status": "draft",
    }
    second_payload = {
        **first_payload,
        "name": "Second Duplicate Venue",
        "slug": "second-duplicate-venue",
        "address": "Jl. Second No.2",
    }
    first = client.post("/api/v1/admin/venues", json=first_payload).json()
    second = client.post("/api/v1/admin/venues", json=second_payload).json()

    duplicate_response = client.patch(
        f"/api/v1/admin/venues/{second['id']}",
        json={
            **second_payload,
            "slug": first["slug"],
        },
    )

    assert duplicate_response.status_code == 409
    assert duplicate_response.json()["error"]["code"] == "slug_conflict"


def test_admin_can_upload_venue_photo_to_r2_storage(
    admin_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.api.v1.endpoints import admin as admin_endpoint

    class FakeVenuePhotoStorage:
        async def upload(
            self,
            *,
            file,
            venue_id: int | None,
            temp_venue_id: str | None,
        ) -> dict:
            assert venue_id is not None
            assert temp_venue_id is None
            contents = await file.read()
            assert contents == b"fake image"
            return {
                "filename": "ballroom.jpg",
                "original_filename": "ballroom.jpg",
                "content_type": "image/jpeg",
                "file_size": len(contents),
                "storage_key": f"venues/{venue_id}/ballroom.jpg",
                "url": f"https://cdn.7magic.test/venues/{venue_id}/ballroom.jpg",
                "thumbnail_url": f"https://cdn.7magic.test/venues/{venue_id}/ballroom.jpg",
                "variants": {
                    "original": f"https://cdn.7magic.test/venues/{venue_id}/ballroom.jpg",
                },
            }

    monkeypatch.setattr(admin_endpoint, "venue_photo_storage", FakeVenuePhotoStorage(), raising=False)

    client = admin_client
    create_payload = {
        "name": "Photo Upload Venue",
        "slug": "photo-upload-venue",
        "city": "jakarta",
        "district": "Jakarta Barat",
        "address": "Jl. Photo No.1",
        "stars": 5,
        "description": "A venue with R2-backed photo uploads.",
        "price_start_from": 128000000,
        "price_for_total_pax": 300,
        "status": "active",
    }
    venue = client.post("/api/v1/admin/venues", json=create_payload).json()

    response = client.post(
        f"/api/v1/admin/venues/{venue['id']}/photos",
        data={"alt_text": "Grand ballroom setup", "sort_order": "3", "set_as_cover": "true"},
        files={"file": ("ballroom.jpg", b"fake image", "image/jpeg")},
    )

    assert response.status_code == 201
    photo = response.json()
    assert photo["id"] >= 1
    assert photo["venue_id"] == venue["id"]
    assert photo["alt_text"] == "Grand ballroom setup"
    assert photo["sort_order"] == 3
    assert photo["url"] == f"https://cdn.7magic.test/venues/{venue['id']}/ballroom.jpg"

    detail = client.get(f"/api/v1/admin/venues/{venue['id']}").json()
    assert detail["cover_photo"]["small_url"] == photo["url"]
    assert detail["gallery"][0]["url"] == photo["url"]


def test_public_articles_default_to_indonesian(public_article_client: TestClient) -> None:
    response = public_article_client.get("/api/v1/public/articles")

    assert response.status_code == 200
    items = response.json()["items"]
    assert items
    assert all(item["locale"] == "id" for item in items)


def test_public_articles_fall_back_to_indonesian_when_no_translation(
    public_article_client: TestClient,
) -> None:
    """An English listing must still surface Indonesian articles that have no
    English sibling, rather than returning an empty page."""
    indonesian = public_article_client.get("/api/v1/public/articles").json()["items"]
    english = public_article_client.get("/api/v1/public/articles?locale=en").json()["items"]

    assert {item["slug"] for item in english} == {item["slug"] for item in indonesian}


def test_public_articles_reject_unknown_locale(public_article_client: TestClient) -> None:
    response = public_article_client.get("/api/v1/public/articles?locale=fr")

    assert response.status_code == 422
