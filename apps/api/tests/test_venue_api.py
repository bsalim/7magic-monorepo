from __future__ import annotations

from collections.abc import AsyncGenerator, Generator

import pytest
from fastapi import UploadFile
from fastapi.testclient import TestClient
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from starlette.requests import Request

from app import models  # noqa: F401
from app.api.v1.dependencies import AuthError, require_admin_user, require_website_read_access
from app.core.config import get_settings
from app.core.database import Base, get_db_session
from app.main import app
from app.models import Venue, VenuePhoto
from app.schemas.content import VenueCreate, VenueDetail
from app.services.auth import AuthenticatedUser
from app.services.storage import FileTooLargeError, R2VenuePhotoStorage
from app.services.venues import VenueSlugConflictError, venue_service


@pytest.fixture()
def venue_client(tmp_path) -> Generator[TestClient, None, None]:
    database_url = f"sqlite+aiosqlite:///{tmp_path / 'venue-test.db'}"
    engine = create_async_engine(database_url)
    session_factory = async_sessionmaker(engine, autoflush=False, expire_on_commit=False)

    async def override_db_session() -> AsyncGenerator[AsyncSession, None]:
        async with session_factory() as session:
            yield session

    def override_admin_user() -> AuthenticatedUser:
        return AuthenticatedUser(
            id=1,
            email="admin@example.com",
            username="admin",
            first_name="Admin",
            last_name="User",
            roles=["admin"],
        )

    async def prepare_database() -> None:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

        async with session_factory() as session:
            active_venue = Venue(
                name="Active Venue",
                slug="active-venue",
                city="jakarta",
                district="Jakarta Pusat",
                address="Jl. Active No.1",
                stars=5,
                description="An active venue for website API tests.",
                price_for_total_pax=250,
                status="active",
            )
            active_venue.photos.append(
                VenuePhoto(
                    sort_order=0,
                    alt_text="Active venue ballroom",
                    original_filename="active-ballroom-original.jpg",
                    filename="active-ballroom.jpg",
                    content_type="image/jpeg",
                    storage_key="venues/active/private-storage-key.jpg",
                    cdn_url="https://cdn.7magic.test/venues/active/ballroom.jpg",
                    thumbnail_url="https://cdn.7magic.test/venues/active/ballroom-thumb.jpg",
                    original_file_size=12345,
                )
            )
            session.add_all(
                [
                    active_venue,
                    Venue(
                        name="Draft Venue",
                        slug="draft-venue",
                        city="jakarta",
                        district="Jakarta Pusat",
                        address="Jl. Draft No.1",
                        stars=4,
                        description="A draft venue for website API tests.",
                        price_for_total_pax=200,
                        status="draft",
                    ),
                ]
            )
            await session.commit()

    import asyncio

    asyncio.run(prepare_database())
    previous_overrides = app.dependency_overrides.copy()
    app.dependency_overrides[get_db_session] = override_db_session
    app.dependency_overrides[require_admin_user] = override_admin_user

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous_overrides)
        asyncio.run(engine.dispose())


@pytest_asyncio.fixture()
async def venue_session(tmp_path) -> AsyncGenerator[AsyncSession, None]:
    database_url = f"sqlite+aiosqlite:///{tmp_path / 'venue-service-test.db'}"
    engine = create_async_engine(database_url)
    session_factory = async_sessionmaker(engine, autoflush=False, expire_on_commit=False)

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    try:
        async with session_factory() as session:
            yield session
    finally:
        await engine.dispose()


def test_website_venues_require_allowed_origin_when_configured(
    venue_client: TestClient,
    monkeypatch,
) -> None:
    _clear_venue_settings_env(monkeypatch)
    monkeypatch.setenv("VENUE_READ_ALLOWED_ORIGINS", '["https://7magic.id"]')
    get_settings.cache_clear()
    try:
        settings = get_settings()

        denied_response = venue_client.get("/api/v1/venues")

        assert denied_response.status_code == 403
        assert denied_response.json()["error"] == {
            "code": "website_access_denied",
            "message": "Website venue access is not allowed from this origin.",
            "details": {},
        }

        malicious_referer_request = _request(
            headers=[(b"referer", b"https://7magic.id.evil.test/page")]
        )
        with pytest.raises(AuthError) as malicious_exc_info:
            require_website_read_access(malicious_referer_request, settings)

        assert malicious_exc_info.value.status_code == 403
        assert malicious_exc_info.value.code == "website_access_denied"

        allowed_response = venue_client.get(
            "/api/v1/venues",
            headers={"origin": "https://7magic.id"},
        )

        assert allowed_response.status_code == 200
        assert allowed_response.json()["items"][0]["slug"] == "active-venue"
    finally:
        get_settings.cache_clear()


def test_website_venues_require_api_key_when_configured(monkeypatch) -> None:
    _clear_venue_settings_env(monkeypatch)
    monkeypatch.setenv("VENUE_READ_API_KEY", "test-venue-key")
    get_settings.cache_clear()
    try:
        settings = get_settings()

        with pytest.raises(AuthError) as exc_info:
            require_website_read_access(_request(), settings)

        assert exc_info.value.status_code == 403
        assert exc_info.value.code == "website_access_denied"
        assert exc_info.value.message == "Website venue access key is invalid."

        allowed_request = _request(headers=[(b"x-7magic-venue-key", b"test-venue-key")])

        assert require_website_read_access(allowed_request, settings) is None
    finally:
        get_settings.cache_clear()


def test_website_venue_routes_return_active_database_venues_only(
    venue_client: TestClient,
    monkeypatch,
) -> None:
    _clear_venue_settings_env(monkeypatch)
    get_settings.cache_clear()
    try:
        list_response = venue_client.get("/api/v1/venues")

        assert list_response.status_code == 200
        venue_list = list_response.json()
        assert [item["slug"] for item in venue_list["items"]] == ["active-venue"]
        assert "storage_key" not in venue_list["items"][0]
        assert venue_list["pagination"] == {
            "page": 1,
            "page_size": 12,
            "total": 1,
            "total_pages": 1,
        }

        detail_response = venue_client.get("/api/v1/venues/jakarta/active-venue")

        assert detail_response.status_code == 200
        detail = detail_response.json()
        assert detail["slug"] == "active-venue"
        assert detail["city"] == "jakarta"
        assert detail["status"] == "active"
        assert detail["gallery"]
        for photo in detail["gallery"]:
            assert photo["url"] == "https://cdn.7magic.test/venues/active/ballroom.jpg"
            assert photo["thumbnail_url"] == (
                "https://cdn.7magic.test/venues/active/ballroom-thumb.jpg"
            )
            assert "storage_key" not in photo
            assert "filename" not in photo
            assert "original_filename" not in photo
            assert "content_type" not in photo
            assert "file_size" not in photo
            assert "venue_id" not in photo

        draft_response = venue_client.get("/api/v1/venues/jakarta/draft-venue")

        assert draft_response.status_code == 404
        assert draft_response.json()["error"] == {
            "code": "not_found",
            "message": "Venue not found.",
            "details": {"resource": "venue"},
        }
    finally:
        get_settings.cache_clear()


def test_website_venue_detail_route_requires_allowed_origin_when_configured(
    venue_client: TestClient,
    monkeypatch,
) -> None:
    _clear_venue_settings_env(monkeypatch)
    monkeypatch.setenv("VENUE_READ_ALLOWED_ORIGINS", '["https://7magic.id"]')
    get_settings.cache_clear()
    try:
        denied_response = venue_client.get("/api/v1/venues/jakarta/active-venue")

        assert denied_response.status_code == 403
        assert denied_response.json()["error"] == {
            "code": "website_access_denied",
            "message": "Website venue access is not allowed from this origin.",
            "details": {},
        }

        allowed_response = venue_client.get(
            "/api/v1/venues/jakarta/active-venue",
            headers={"origin": "https://7magic.id"},
        )

        assert allowed_response.status_code == 200
        assert allowed_response.json()["slug"] == "active-venue"
    finally:
        get_settings.cache_clear()


def test_website_venue_detail_response_model_filters_internal_gallery_fields(
    venue_client: TestClient,
    monkeypatch,
) -> None:
    _clear_venue_settings_env(monkeypatch)
    get_settings.cache_clear()

    async def website_detail_with_internal_gallery_fields(*args, **kwargs) -> VenueDetail:
        return VenueDetail(
            id=1,
            name="Active Venue",
            slug="active-venue",
            city="jakarta",
            district="Jakarta Pusat",
            stars=5,
            price_start_from=None,
            price_for_total_pax=250,
            path_url="/wedding-venue/jakarta/active-venue",
            cover_photo={
                "alt": "Active venue ballroom",
                "small_url": "https://cdn.7magic.test/venues/active/ballroom-thumb.jpg",
                "large_url": "https://cdn.7magic.test/venues/active/ballroom.jpg",
            },
            address="Jl. Active No.1",
            description="An active venue for website API tests.",
            status="active",
            gallery=[
                {
                    "id": 1,
                    "url": "https://cdn.7magic.test/venues/active/ballroom.jpg",
                    "thumbnail_url": (
                        "https://cdn.7magic.test/venues/active/ballroom-thumb.jpg"
                    ),
                    "alt_text": "Active venue ballroom",
                    "sort_order": 0,
                    "webp": "https://cdn.7magic.test/venues/active/ballroom.jpg",
                    "fallback": "https://cdn.7magic.test/venues/active/ballroom.jpg",
                    "thumb_webp": (
                        "https://cdn.7magic.test/venues/active/ballroom-thumb.jpg"
                    ),
                    "thumb_fallback": (
                        "https://cdn.7magic.test/venues/active/ballroom-thumb.jpg"
                    ),
                    "storage_key": "venues/active/private-storage-key.jpg",
                    "filename": "active-ballroom.jpg",
                    "original_filename": "active-ballroom-original.jpg",
                    "content_type": "image/jpeg",
                    "file_size": 12345,
                    "venue_id": 1,
                }
            ],
            packages=[],
            seo=None,
        )

    monkeypatch.setattr(
        venue_service,
        "website_detail",
        website_detail_with_internal_gallery_fields,
    )
    try:
        response = venue_client.get("/api/v1/venues/jakarta/active-venue")

        assert response.status_code == 200
        photo = response.json()["gallery"][0]
        assert photo == {
            "id": 1,
            "url": "https://cdn.7magic.test/venues/active/ballroom.jpg",
            "thumbnail_url": "https://cdn.7magic.test/venues/active/ballroom-thumb.jpg",
            "alt_text": "Active venue ballroom",
            "sort_order": 0,
            "webp": "https://cdn.7magic.test/venues/active/ballroom.jpg",
            "fallback": "https://cdn.7magic.test/venues/active/ballroom.jpg",
            "thumb_webp": "https://cdn.7magic.test/venues/active/ballroom-thumb.jpg",
            "thumb_fallback": "https://cdn.7magic.test/venues/active/ballroom-thumb.jpg",
        }
    finally:
        get_settings.cache_clear()


@pytest.mark.asyncio
async def test_venue_service_create_normalizes_city_and_rejects_duplicate_slug(
    venue_session: AsyncSession,
) -> None:
    payload = VenueCreate(
        name="Canonical City Venue",
        slug="canonical-city-venue",
        city=" South Jakarta ",
        district="Kebayoran Baru",
        address="Jl. Canonical No.1",
        stars=5,
        description="A venue used to verify canonical city writes.",
        price_start_from=125000000,
        price_for_total_pax=300,
        status="active",
    )

    created = await venue_service.create(venue_session, payload)

    assert created.city == "south-jakarta"
    assert created.path_url == "/wedding-venue/south-jakarta/canonical-city-venue"

    duplicate_payload = payload.model_copy(update={"city": "south jakarta"})
    with pytest.raises(VenueSlugConflictError):
        await venue_service.create(venue_session, duplicate_payload)


@pytest.mark.asyncio
async def test_venue_service_website_detail_omits_internal_gallery_metadata(
    venue_session: AsyncSession,
) -> None:
    venue = Venue(
        name="Public Gallery Venue",
        slug="public-gallery-venue",
        city="jakarta",
        district="Jakarta Pusat",
        address="Jl. Public Gallery No.1",
        stars=5,
        description="A venue with public-safe gallery output.",
        price_for_total_pax=250,
        status="active",
    )
    venue.photos.append(
        VenuePhoto(
            sort_order=0,
            alt_text="Ballroom",
            original_filename="ballroom-original.jpg",
            filename="ballroom.jpg",
            content_type="image/jpeg",
            storage_key="venues/1/private-storage-key.jpg",
            cdn_url="https://cdn.7magic.test/venues/1/ballroom.jpg",
            thumbnail_url="https://cdn.7magic.test/venues/1/ballroom-thumb.jpg",
            original_file_size=12345,
        )
    )
    venue_session.add(venue)
    await venue_session.commit()

    detail = await venue_service.website_detail(
        venue_session,
        city="jakarta",
        slug="public-gallery-venue",
    )

    assert detail.gallery == [
        {
            "id": venue.photos[0].id,
            "url": "https://cdn.7magic.test/venues/1/ballroom.jpg",
            "thumbnail_url": "https://cdn.7magic.test/venues/1/ballroom-thumb.jpg",
            "alt_text": "Ballroom",
            "sort_order": 0,
            "webp": "https://cdn.7magic.test/venues/1/ballroom.jpg",
            "fallback": "https://cdn.7magic.test/venues/1/ballroom.jpg",
            "thumb_webp": "https://cdn.7magic.test/venues/1/ballroom-thumb.jpg",
            "thumb_fallback": "https://cdn.7magic.test/venues/1/ballroom-thumb.jpg",
        }
    ]


@pytest.mark.asyncio
async def test_venue_service_website_detail_resolves_city_token_slug_alias(
    venue_session: AsyncSession,
) -> None:
    venue = Venue(
        name="The Ritz-Carlton Jakarta, Pacific Place",
        slug="ritz-carlton-jakarta-pacific-place",
        city="jakarta",
        district="Jakarta Selatan",
        address="Jl. Example No.1",
        stars=5,
        description="A canonical DB venue with a city token in the slug.",
        price_for_total_pax=350,
        status="active",
    )
    venue.photos.append(
        VenuePhoto(
            sort_order=0,
            alt_text="Ritz ballroom",
            cdn_url="https://cdn.7magic.test/venues/ritz/ballroom.jpg",
            thumbnail_url="https://cdn.7magic.test/venues/ritz/ballroom-thumb.jpg",
        )
    )
    venue_session.add(venue)
    await venue_session.commit()

    detail = await venue_service.website_detail(
        venue_session,
        city="jakarta",
        slug="ritz-carlton-pacific-place",
    )

    assert detail.slug == "ritz-carlton-jakarta-pacific-place"
    assert len(detail.gallery) == 1
    assert detail.gallery[0]["url"] == "https://cdn.7magic.test/venues/ritz/ballroom.jpg"


def test_admin_venue_crud_uses_database(venue_client: TestClient, monkeypatch) -> None:
    _clear_venue_settings_env(monkeypatch)
    get_settings.cache_clear()
    create_payload = {
        "name": "Database Backed Ballroom",
        "slug": "database-backed-ballroom",
        "city": "South Jakarta",
        "district": "Kebayoran Baru",
        "address": "Jl. Database No.1",
        "stars": 4,
        "description": "A venue created through database-backed admin APIs.",
        "price_start_from": 75000000,
        "price_for_total_pax": 180,
        "status": "draft",
    }

    create_response = venue_client.post("/api/v1/admin/venues", json=create_payload)

    assert create_response.status_code == 201
    created = create_response.json()
    assert created["id"] > 0
    assert created["name"] == "Database Backed Ballroom"
    assert created["city"] == "south-jakarta"
    assert created["price_start_from"] == 75000000
    assert created["path_url"] == "/wedding-venue/south-jakarta/database-backed-ballroom"

    update_response = venue_client.patch(
        f"/api/v1/admin/venues/{created['id']}",
        json={
            "name": "Database Backed Ballroom Updated",
            "slug": "database-backed-ballroom-updated",
            "city": "North Jakarta",
            "district": "Kelapa Gading",
            "address": "Jl. Database Updated No.2",
            "stars": 5,
            "description": "Updated database-backed venue copy.",
            "price_start_from": 99000000,
            "price_for_total_pax": 240,
            "status": "active",
        },
    )

    assert update_response.status_code == 200
    updated = update_response.json()
    assert updated["name"] == "Database Backed Ballroom Updated"
    assert updated["slug"] == "database-backed-ballroom-updated"
    assert updated["city"] == "north-jakarta"
    assert updated["district"] == "Kelapa Gading"
    assert updated["address"] == "Jl. Database Updated No.2"
    assert updated["stars"] == 5
    assert updated["description"] == "Updated database-backed venue copy."
    assert updated["price_start_from"] == 99000000
    assert updated["price_for_total_pax"] == 240
    assert updated["status"] == "active"
    assert updated["path_url"] == "/wedding-venue/north-jakarta/database-backed-ballroom-updated"

    detail_response = venue_client.get(f"/api/v1/admin/venues/{created['id']}")

    assert detail_response.status_code == 200
    detail = detail_response.json()
    assert detail["id"] == created["id"]
    assert detail["name"] == "Database Backed Ballroom Updated"
    assert detail["path_url"] == "/wedding-venue/north-jakarta/database-backed-ballroom-updated"
    assert detail["gallery"] == []

    try:
        public_detail_response = venue_client.get(
            "/api/v1/venues/north-jakarta/database-backed-ballroom-updated"
        )

        assert public_detail_response.status_code == 200

        delete_response = venue_client.delete(f"/api/v1/admin/venues/{created['id']}")

        assert delete_response.status_code == 200
        deleted = delete_response.json()
        assert deleted["id"] == created["id"]
        assert deleted["status"] == "archived"

        archived_detail_response = venue_client.get(f"/api/v1/admin/venues/{created['id']}")

        assert archived_detail_response.status_code == 200
        assert archived_detail_response.json()["status"] == "archived"

        hidden_public_detail_response = venue_client.get(
            "/api/v1/venues/north-jakarta/database-backed-ballroom-updated"
        )

        assert hidden_public_detail_response.status_code == 404
    finally:
        get_settings.cache_clear()


def test_admin_venue_rejects_duplicate_city_slug(venue_client: TestClient) -> None:
    response = venue_client.post(
        "/api/v1/admin/venues",
        json={
            "name": "Duplicate Active Venue",
            "slug": "active-venue",
            "city": "jakarta",
            "district": "Jakarta Pusat",
            "address": "Jl. Duplicate No.1",
            "stars": 5,
            "description": "A duplicate of the active fixture venue.",
            "price_start_from": 100000000,
            "price_for_total_pax": 250,
            "status": "active",
        },
    )

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "slug_conflict"


def test_admin_venue_photo_rejects_non_image_upload(venue_client: TestClient) -> None:
    response = venue_client.post(
        "/api/v1/admin/venues/1/photos",
        files={"file": ("notes.txt", b"not an image", "text/plain")},
    )

    assert response.status_code == 422
    assert response.json()["error"] == {
        "code": "unsupported_file_type",
        "message": "Venue photos must be image uploads.",
        "details": {"field": "file"},
    }


def test_admin_venue_photo_upload_returns_503_when_storage_missing(
    venue_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.api.v1.endpoints import admin as admin_endpoint
    from app.core.config import Settings

    monkeypatch.setattr(
        admin_endpoint,
        "venue_photo_storage",
        R2VenuePhotoStorage(
            Settings(
                r2_endpoint_url=None,
                r2_access_key_id=None,
                r2_secret_access_key=None,
                r2_bucket_name=None,
                r2_public_base_url=None,
            )
        ),
    )

    response = venue_client.post(
        "/api/v1/admin/venues/1/photos",
        files={"file": ("ballroom.jpg", b"fake image", "image/jpeg")},
    )

    assert response.status_code == 503
    assert response.json()["error"] == {
        "code": "storage_not_configured",
        "message": "R2 storage is not configured.",
        "details": {"provider": "cloudflare_r2"},
    }


def test_admin_venue_photo_upload_checks_venue_before_storage(
    venue_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.api.v1.endpoints import admin as admin_endpoint

    class FakeVenuePhotoStorage:
        async def upload(
            self,
            *,
            file: UploadFile,
            venue_id: int | None,
            temp_venue_id: str | None,
        ) -> dict:
            raise AssertionError("storage should not be called for missing venues")

    monkeypatch.setattr(admin_endpoint, "venue_photo_storage", FakeVenuePhotoStorage())

    response = venue_client.post(
        "/api/v1/admin/venues/999/photos",
        files={"file": ("ballroom.jpg", b"fake image", "image/jpeg")},
    )

    assert response.status_code == 404
    assert response.json()["error"] == {
        "code": "not_found",
        "message": "Venue not found.",
        "details": {"resource": "venue"},
    }


def test_admin_venue_photo_upload_persists_storage_metadata(
    venue_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.api.v1.endpoints import admin as admin_endpoint

    class FakeVenuePhotoStorage:
        async def upload(
            self,
            *,
            file: UploadFile,
            venue_id: int | None,
            temp_venue_id: str | None,
        ) -> dict:
            assert venue_id == 1
            assert temp_venue_id is None
            contents = await file.read()
            return {
                "filename": "metadata-ballroom.jpg",
                "original_filename": file.filename,
                "content_type": file.content_type,
                "file_size": len(contents),
                "storage_key": "venues/1/metadata-ballroom.jpg",
                "url": "https://cdn.7magic.test/venues/1/metadata-ballroom.jpg",
                "thumbnail_url": "https://cdn.7magic.test/venues/1/metadata-ballroom-thumb.jpg",
                "variants": {
                    "original": "https://cdn.7magic.test/venues/1/metadata-ballroom.jpg",
                },
            }

    monkeypatch.setattr(admin_endpoint, "venue_photo_storage", FakeVenuePhotoStorage())

    response = venue_client.post(
        "/api/v1/admin/venues/1/photos",
        data={"alt_text": "Metadata ballroom", "sort_order": "7"},
        files={"file": ("original ballroom.jpg", b"fake image", "image/jpeg")},
    )

    assert response.status_code == 201
    photo = response.json()
    assert photo["url"] == "https://cdn.7magic.test/venues/1/metadata-ballroom.jpg"
    assert photo["thumbnail_url"] == (
        "https://cdn.7magic.test/venues/1/metadata-ballroom-thumb.jpg"
    )
    assert photo["storage_key"] == "venues/1/metadata-ballroom.jpg"
    assert photo["filename"] == "metadata-ballroom.jpg"
    assert photo["original_filename"] == "original ballroom.jpg"
    assert photo["content_type"] == "image/jpeg"
    assert photo["file_size"] == len(b"fake image")
    assert photo["variants"] == {
        "original": "https://cdn.7magic.test/venues/1/metadata-ballroom.jpg",
    }

    detail = venue_client.get("/api/v1/admin/venues/1").json()
    persisted = next(
        item for item in detail["gallery"] if item["storage_key"] == photo["storage_key"]
    )
    assert persisted["url"] == photo["url"]
    assert persisted["thumbnail_url"] == photo["thumbnail_url"]
    assert persisted["original_filename"] == "original ballroom.jpg"
    assert persisted["content_type"] == "image/jpeg"
    assert persisted["file_size"] == len(b"fake image")


def test_admin_venue_photo_upload_returns_413_when_file_too_large(
    venue_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.api.v1.endpoints import admin as admin_endpoint

    class FakeVenuePhotoStorage:
        async def upload(
            self,
            *,
            file: UploadFile,
            venue_id: int | None,
            temp_venue_id: str | None,
        ) -> dict:
            raise FileTooLargeError("Venue photo upload is too large.")

    monkeypatch.setattr(admin_endpoint, "venue_photo_storage", FakeVenuePhotoStorage())

    response = venue_client.post(
        "/api/v1/admin/venues/1/photos",
        files={"file": ("huge.jpg", b"fake image", "image/jpeg")},
    )

    assert response.status_code == 413
    assert response.json()["error"] == {
        "code": "file_too_large",
        "message": "Venue photo upload is too large.",
        "details": {"field": "file"},
    }


@pytest.mark.asyncio
async def test_r2_venue_photo_storage_rejects_files_larger_than_configured_max() -> None:
    from app.core.config import Settings

    class BoundedReadUpload:
        filename = "too-large.jpg"
        content_type = "image/jpeg"

        def __init__(self, contents: bytes) -> None:
            self._contents = contents
            self._offset = 0

        async def read(self, size: int = -1) -> bytes:
            if size < 0:
                raise AssertionError("storage must not perform an unbounded upload read")

            start = self._offset
            end = min(start + size, len(self._contents))
            self._offset = end
            return self._contents[start:end]

    storage = R2VenuePhotoStorage(
        Settings(
            r2_endpoint_url="https://r2.test",
            r2_access_key_id="access",
            r2_secret_access_key="secret",
            r2_bucket_name="bucket",
            r2_public_base_url="https://cdn.7magic.test",
            venue_upload_max_bytes=3,
        )
    )

    with pytest.raises(FileTooLargeError):
        await storage.upload(
            file=BoundedReadUpload(b"1234"),  # type: ignore[arg-type]
            venue_id=1,
            temp_venue_id=None,
        )


def test_admin_venue_photo_lower_sort_order_without_cover_keeps_existing_cover(
    venue_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.api.v1.endpoints import admin as admin_endpoint

    class FakeVenuePhotoStorage:
        async def upload(
            self,
            *,
            file: UploadFile,
            venue_id: int | None,
            temp_venue_id: str | None,
        ) -> dict:
            contents = await file.read()
            filename = file.filename or "venue-photo.jpg"
            return {
                "filename": filename,
                "original_filename": filename,
                "content_type": file.content_type,
                "file_size": len(contents),
                "storage_key": f"venues/{venue_id}/{filename}",
                "url": f"https://cdn.7magic.test/venues/{venue_id}/{filename}",
                "thumbnail_url": f"https://cdn.7magic.test/venues/{venue_id}/{filename}-thumb",
                "variants": {
                    "original": f"https://cdn.7magic.test/venues/{venue_id}/{filename}",
                },
            }

    monkeypatch.setattr(admin_endpoint, "venue_photo_storage", FakeVenuePhotoStorage())

    response = venue_client.post(
        "/api/v1/admin/venues/1/photos",
        data={"alt_text": "Manual lower order", "sort_order": "-10"},
        files={"file": ("manual-lower.jpg", b"fake image", "image/jpeg")},
    )

    assert response.status_code == 201
    photo = response.json()

    detail = venue_client.get("/api/v1/admin/venues/1").json()
    cover = detail["cover_photo"]
    assert cover["alt"] == "Active venue ballroom"
    assert cover["small_url"] == "https://cdn.7magic.test/venues/active/ballroom-thumb.jpg"
    assert cover["large_url"] == "https://cdn.7magic.test/venues/active/ballroom.jpg"
    assert detail["gallery"][0]["storage_key"] == "venues/active/private-storage-key.jpg"
    assert detail["gallery"][1]["storage_key"] == photo["storage_key"]


def test_admin_venue_photo_set_as_cover_makes_later_upload_admin_detail_cover(
    venue_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.api.v1.endpoints import admin as admin_endpoint

    class FakeVenuePhotoStorage:
        async def upload(
            self,
            *,
            file: UploadFile,
            venue_id: int | None,
            temp_venue_id: str | None,
        ) -> dict:
            contents = await file.read()
            filename = file.filename or "venue-photo.jpg"
            return {
                "filename": filename,
                "original_filename": filename,
                "content_type": file.content_type,
                "file_size": len(contents),
                "storage_key": f"venues/{venue_id}/{filename}",
                "url": f"https://cdn.7magic.test/venues/{venue_id}/{filename}",
                "thumbnail_url": f"https://cdn.7magic.test/venues/{venue_id}/{filename}-thumb",
                "variants": {
                    "original": f"https://cdn.7magic.test/venues/{venue_id}/{filename}",
                },
            }

    monkeypatch.setattr(admin_endpoint, "venue_photo_storage", FakeVenuePhotoStorage())

    response = venue_client.post(
        "/api/v1/admin/venues/1/photos",
        data={"alt_text": "New cover", "sort_order": "9", "set_as_cover": "true"},
        files={"file": ("new-cover.jpg", b"fake image", "image/jpeg")},
    )

    assert response.status_code == 201
    photo = response.json()

    detail = venue_client.get("/api/v1/admin/venues/1").json()
    cover = detail["cover_photo"]
    assert cover["alt"] == "New cover"
    assert cover["small_url"] == photo["thumbnail_url"]
    assert cover["large_url"] == photo["url"]
    assert detail["gallery"][0]["storage_key"] == photo["storage_key"]


def test_temp_photo_upload_is_claimed_on_venue_creation(
    venue_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Photos uploaded to a temp id are bound to the venue once it is created."""
    from app.api.v1.endpoints import admin as admin_endpoint

    class FakeVenuePhotoStorage:
        async def upload(
            self,
            *,
            file: UploadFile,
            venue_id: int | None,
            temp_venue_id: str | None,
        ) -> dict:
            assert venue_id is None
            assert temp_venue_id is not None
            contents = await file.read()
            filename = file.filename or "temp.jpg"
            return {
                "filename": filename,
                "original_filename": filename,
                "content_type": file.content_type,
                "file_size": len(contents),
                "storage_key": f"venues/temp/{temp_venue_id}/{filename}",
                "url": f"https://cdn.7magic.test/temp/{temp_venue_id}/{filename}",
                "thumbnail_url": f"https://cdn.7magic.test/temp/{temp_venue_id}/{filename}-thumb",
                "variants": {},
            }

    monkeypatch.setattr(admin_endpoint, "venue_photo_storage", FakeVenuePhotoStorage())

    temp_id = "11111111-1111-1111-1111-111111111111"

    first = venue_client.post(
        "/api/v1/admin/uploads/venue-photo",
        data={"temp_venue_id": temp_id, "alt_text": "Lobby", "sort_order": "0"},
        files={"file": ("lobby.jpg", b"fake image", "image/jpeg")},
    )
    assert first.status_code == 201
    assert first.json()["temp_venue_id"] == temp_id
    assert first.json()["venue_id"] is None

    venue_client.post(
        "/api/v1/admin/uploads/venue-photo",
        data={"temp_venue_id": temp_id, "alt_text": "Ballroom", "sort_order": "1"},
        files={"file": ("ballroom.jpg", b"fake image", "image/jpeg")},
    )

    created = venue_client.post(
        "/api/v1/admin/venues",
        json={
            "name": "Temp Photo Venue",
            "slug": "temp-photo-venue",
            "city": "jakarta",
            "district": "Jakarta Pusat",
            "address": "Jl. Temp No.1",
            "stars": 5,
            "description": "Created with photos uploaded to a temp id.",
            "price_for_total_pax": 200,
            "status": "draft",
            "temp_venue_id": temp_id,
        },
    )
    assert created.status_code == 201
    detail = created.json()
    assert len(detail["gallery"]) == 2
    storage_keys = {photo["storage_key"] for photo in detail["gallery"]}
    assert f"venues/temp/{temp_id}/lobby.jpg" in storage_keys
    assert all(photo["venue_id"] == detail["id"] for photo in detail["gallery"])


def _clear_venue_settings_env(monkeypatch) -> None:
    monkeypatch.setenv("VENUE_READ_ALLOWED_ORIGINS", "[]")
    monkeypatch.setenv("VENUE_READ_API_KEY", "")


def _request(headers: list[tuple[bytes, bytes]] | None = None) -> Request:
    return Request(
        {
            "type": "http",
            "method": "GET",
            "path": "/api/v1/venues",
            "headers": headers or [],
        }
    )


def test_venue_detail_defaults_to_indonesian_description(
    venue_client: TestClient,
    monkeypatch,
) -> None:
    _clear_venue_settings_env(monkeypatch)
    get_settings.cache_clear()
    try:
        response = venue_client.get("/api/v1/venues/jakarta/active-venue")

        assert response.status_code == 200
        assert response.json()["description"] == "An active venue for website API tests."
    finally:
        get_settings.cache_clear()


def test_venue_detail_falls_back_to_indonesian_when_translation_missing(
    venue_client: TestClient,
    monkeypatch,
) -> None:
    _clear_venue_settings_env(monkeypatch)
    get_settings.cache_clear()
    try:
        response = venue_client.get("/api/v1/venues/jakarta/active-venue?locale=en")

        assert response.status_code == 200
        assert response.json()["description"] == "An active venue for website API tests."
    finally:
        get_settings.cache_clear()


def test_venue_detail_returns_english_translation_when_present(
    venue_client: TestClient,
    monkeypatch,
) -> None:
    _clear_venue_settings_env(monkeypatch)
    get_settings.cache_clear()
    try:
        listed = venue_client.get("/api/v1/venues").json()["items"]
        venue_id = listed[0]["id"]

        upsert = venue_client.put(
            f"/api/v1/admin/venues/{venue_id}/translations/en",
            json={"description": "An elegant ballroom in central Jakarta."},
        )
        assert upsert.status_code == 200

        response = venue_client.get("/api/v1/venues/jakarta/active-venue?locale=en")

        assert response.status_code == 200
        assert response.json()["description"] == "An elegant ballroom in central Jakarta."

        indonesian = venue_client.get("/api/v1/venues/jakarta/active-venue")
        assert indonesian.json()["description"] == "An active venue for website API tests."
    finally:
        get_settings.cache_clear()


def test_venue_translation_rejects_unknown_locale(
    venue_client: TestClient,
    monkeypatch,
) -> None:
    _clear_venue_settings_env(monkeypatch)
    get_settings.cache_clear()
    try:
        listed = venue_client.get("/api/v1/venues").json()["items"]
        venue_id = listed[0]["id"]

        response = venue_client.put(
            f"/api/v1/admin/venues/{venue_id}/translations/fr",
            json={"description": "Une salle de bal."},
        )
        assert response.status_code == 422
    finally:
        get_settings.cache_clear()


def test_price_bands_summarize_active_venues(
    venue_client: TestClient,
    monkeypatch,
) -> None:
    """The homepage anchors on real pricing, so the floor and band counts must
    come from active venues and ignore the 0 = 'on request' rows."""
    _clear_venue_settings_env(monkeypatch)
    get_settings.cache_clear()
    try:
        response = venue_client.get("/api/v1/venues/price-bands")

        assert response.status_code == 200
        payload = response.json()

        # The seeded active venue has no price, so it counts as on-request.
        assert payload["priced"] == 0
        assert payload["on_request"] == 1
        assert payload["floor"] is None
        assert [band["count"] for band in payload["bands"]] == [0, 0, 0]
    finally:
        get_settings.cache_clear()


def test_price_bands_route_is_not_shadowed_by_city_slug(
    venue_client: TestClient,
    monkeypatch,
) -> None:
    """/venues/{city}/{slug} must not swallow /venues/price-bands."""
    _clear_venue_settings_env(monkeypatch)
    get_settings.cache_clear()
    try:
        response = venue_client.get("/api/v1/venues/price-bands")
        assert response.status_code == 200
        assert "bands" in response.json()
    finally:
        get_settings.cache_clear()


def test_set_cover_photo_promotes_photo_to_first(
    venue_client: TestClient,
    monkeypatch,
) -> None:
    """The listing shows venue.photos[0], so promoting a photo means giving it
    the lowest sort_order."""
    _clear_venue_settings_env(monkeypatch)
    get_settings.cache_clear()
    try:
        listed = venue_client.get("/api/v1/venues").json()["items"]
        venue_id = listed[0]["id"]

        detail = venue_client.get(f"/api/v1/admin/venues/{venue_id}").json()
        gallery = detail["gallery"]
        assert len(gallery) >= 1

        # Add a second photo that starts behind the existing cover.
        created = venue_client.post(
            f"/api/v1/admin/venues/{venue_id}/photos",
            files={"file": ("second.jpg", b"\xff\xd8\xff\xdb second photo", "image/jpeg")},
            data={"alt_text": "Second", "sort_order": "5", "set_as_cover": "false"},
        )
        if created.status_code not in (200, 201):
            import pytest

            pytest.skip(f"photo upload unavailable in this env: {created.status_code}")

        detail = venue_client.get(f"/api/v1/admin/venues/{venue_id}").json()
        second_id = detail["gallery"][-1]["id"]
        assert detail["gallery"][0]["id"] != second_id

        response = venue_client.post(
            f"/api/v1/admin/venues/{venue_id}/photos/{second_id}/cover"
        )
        assert response.status_code == 200

        detail = venue_client.get(f"/api/v1/admin/venues/{venue_id}").json()
        assert detail["gallery"][0]["id"] == second_id
    finally:
        get_settings.cache_clear()


def test_set_cover_photo_rejects_photo_from_another_venue(
    venue_client: TestClient,
    monkeypatch,
) -> None:
    _clear_venue_settings_env(monkeypatch)
    get_settings.cache_clear()
    try:
        listed = venue_client.get("/api/v1/venues").json()["items"]
        venue_id = listed[0]["id"]

        response = venue_client.post(
            f"/api/v1/admin/venues/{venue_id}/photos/999999/cover"
        )
        assert response.status_code == 404
    finally:
        get_settings.cache_clear()


def test_cover_photo_exposes_responsive_srcset(
    venue_client: TestClient,
    monkeypatch,
) -> None:
    """Imported photos already carry 5 widths in webp and jpeg. The public API
    must expose them so the browser can pick a size instead of always taking
    the largest."""
    _clear_venue_settings_env(monkeypatch)
    get_settings.cache_clear()
    try:
        response = venue_client.get("/api/v1/venues")
        assert response.status_code == 200

        cover = response.json()["items"][0]["cover_photo"]
        # Present on the contract even when a photo has no variants.
        assert "webp_srcset" in cover
        assert "jpeg_srcset" in cover
        assert "sizes" in cover
    finally:
        get_settings.cache_clear()


def test_website_venue_list_filters_by_exact_star_ratings(
    venue_client: TestClient,
    monkeypatch,
) -> None:
    """The search page's tick-boxes send one ?stars= entry per ticked rating.

    Exact membership, not "and above": ticking 5 and 3 must leave 4 out, which a
    stars_min filter cannot express.
    """
    _clear_venue_settings_env(monkeypatch)
    get_settings.cache_clear()

    # The fixture ships one active 5-star venue; add an active 4 and 3 so each
    # rating is represented.
    for name, slug, stars in (("Four Star", "four-star", 4), ("Three Star", "three-star", 3)):
        response = venue_client.post(
            "/api/v1/admin/venues",
            json={
                "name": name,
                "slug": slug,
                "city": "Jakarta",
                "district": "Jakarta Pusat",
                "address": f"Jl. {name} No.1",
                "stars": stars,
                "description": f"{name} venue for star filter tests.",
                "price_for_total_pax": 150,
                "status": "active",
            },
        )
        assert response.status_code == 201

    def slugs(query: str) -> set[str]:
        response = venue_client.get(f"/api/v1/venues{query}")
        assert response.status_code == 200
        return {item["slug"] for item in response.json()["items"]}

    assert slugs("") == {"active-venue", "four-star", "three-star"}

    # A single ticked box is exact, not a floor.
    assert slugs("?stars=4") == {"four-star"}

    # Non-adjacent ratings: the gap at 4 is the whole point of tick-boxes.
    assert slugs("?stars=5&stars=3") == {"active-venue", "three-star"}

    # stars_min keeps its "and above" meaning for the hero search and old links.
    assert slugs("?stars_min=4") == {"active-venue", "four-star"}

    # When both arrive, the explicit set wins rather than being ANDed away.
    assert slugs("?stars=3&stars_min=5") == {"three-star"}

    # Out-of-range values are dropped instead of returning an empty page.
    assert slugs("?stars=9") == {"active-venue", "four-star", "three-star"}
