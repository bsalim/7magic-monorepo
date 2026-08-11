from __future__ import annotations

import logging
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, Path, UploadFile, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import require_admin_user
from app.services.articles import (
    ArticleNotFoundError,
    ArticleSlugConflictError,
    article_service,
)
from app.services.promotions import promotion_service
from app.services.showcases import (
    ShowcaseNotFoundError,
    ShowcaseSlugConflictError,
    showcase_image_variants,
    showcase_service,
)
from app.core.config import get_settings
from app.core.database import get_db_session
from app.core.errors import error_response
from app.models import ArticleImage
from app.schemas.content import (
    ArticleAdminDetail,
    ArticleAdminListResponse,
    ArticleCreate,
    ArticleUpdate,
    Locale,
    PromotionPopupAdmin,
    PromotionPopupUpdate,
    ShowcaseAdminDetail,
    ShowcaseAdminListResponse,
    ShowcaseCreate,
    ShowcaseUpdate,
    VenueCreate,
    VenueTranslationResponse,
    VenueTranslationUpsert,
    VenueUpdate,
)
from app.services.auth import AuthenticatedUser
from app.services.leads import lead_service
from app.services.catalog import catalog_service
from app.services.storage import (
    FileTooLargeError,
    R2VenuePhotoStorage,
    StorageNotConfiguredError,
    StorageUploadError,
)
from app.services.venues import VenueNotFoundError, VenueSlugConflictError, venue_service

router = APIRouter(dependencies=[Depends(require_admin_user)])
venue_photo_storage = R2VenuePhotoStorage(get_settings())

DbSession = Annotated[AsyncSession, Depends(get_db_session)]


def _venue_not_found() -> dict:
    return error_response(
        status_code=status.HTTP_404_NOT_FOUND,
        code="not_found",
        message="Venue not found.",
        details={"resource": "venue"},
    )


def _slug_conflict() -> dict:
    return error_response(
        status_code=status.HTTP_409_CONFLICT,
        code="slug_conflict",
        message="Venue slug already exists for this city.",
        details={"field": "slug"},
    )


def _storage_upload_failed() -> dict:
    return error_response(
        status_code=status.HTTP_502_BAD_GATEWAY,
        code="storage_upload_failed",
        message="The image could not be stored. Check object-storage credentials.",
        details={"provider": "cloudflare_r2"},
    )


@router.get("/dashboard")
async def dashboard(session: DbSession) -> dict:
    # catalog_service still supplies the recent-activity feed, but every total
    # comes from the database -- the fixture numbers were unrelated to the real
    # content and reported a hard-coded 18 leads.
    summary = catalog_service.admin_dashboard()

    venue_counts = await venue_service.count(session)
    article_counts = await article_service.count(session)

    summary["totals"]["venues"] = venue_counts["total"]
    summary["totals"]["articles"] = article_counts["total"]
    summary["totals"]["drafts"] = article_counts["draft"]
    summary["totals"]["leads"] = await lead_service.count(session)
    summary["venues"] = venue_counts
    summary["articles"] = article_counts
    return summary


@router.get("/venues")
async def venues(session: DbSession) -> dict:
    items = await venue_service.admin_list(session)
    return {"items": [venue.model_dump() for venue in items]}


@router.get("/venues/{venue_id}")
async def venue_detail(venue_id: int, session: DbSession) -> dict:
    try:
        return (await venue_service.admin_detail(session, venue_id)).model_dump()
    except VenueNotFoundError:
        return _venue_not_found()


@router.post("/venues", status_code=status.HTTP_201_CREATED)
async def create_venue(payload: VenueCreate, session: DbSession) -> dict:
    try:
        return (await venue_service.create(session, payload)).model_dump()
    except VenueSlugConflictError:
        return _slug_conflict()


@router.patch("/venues/{venue_id}")
async def update_venue(venue_id: int, payload: VenueUpdate, session: DbSession) -> dict:
    try:
        return (await venue_service.update(session, venue_id, payload)).model_dump()
    except VenueSlugConflictError:
        return _slug_conflict()
    except VenueNotFoundError:
        return _venue_not_found()


@router.delete("/venues/{venue_id}")
async def delete_venue(venue_id: int, session: DbSession) -> dict:
    try:
        return (await venue_service.archive(session, venue_id)).model_dump()
    except VenueNotFoundError:
        return _venue_not_found()


@router.get("/venues/{venue_id}/translations/{locale}")
async def get_venue_translation(
    session: DbSession,
    venue_id: int,
    locale: Annotated[Locale, Path()],
) -> VenueTranslationResponse | dict:
    try:
        return await venue_service.get_translation(session, venue_id, locale)
    except VenueNotFoundError:
        return _venue_not_found()


@router.put("/venues/{venue_id}/translations/{locale}")
async def upsert_venue_translation(
    session: DbSession,
    payload: VenueTranslationUpsert,
    venue_id: int,
    locale: Annotated[Locale, Path()],
) -> VenueTranslationResponse | dict:
    """Create or update one locale's copy for a venue. Indonesian lives on the
    venue row itself, so only non-base locales are stored here."""
    try:
        return await venue_service.upsert_translation(session, venue_id, locale, payload)
    except VenueNotFoundError:
        return _venue_not_found()


@router.post("/venues/{venue_id}/photos", status_code=status.HTTP_201_CREATED)
async def upload_venue_photo(
    venue_id: int,
    session: DbSession,
    file: UploadFile = File(...),
    alt_text: str | None = Form(default=None),
    sort_order: int = Form(default=0),
    set_as_cover: bool = Form(default=False),
) -> dict:
    if not _is_image_upload(file):
        return error_response(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            code="unsupported_file_type",
            message="Venue photos must be image uploads.",
            details={"field": "file"},
        )

    try:
        await venue_service.admin_detail(session, venue_id)
        storage_result = await venue_photo_storage.upload(
            file=file,
            venue_id=venue_id,
            temp_venue_id=None,
        )
        return (
            await venue_service.attach_photo(
                session,
                venue_id=venue_id,
                storage_result=storage_result,
                alt_text=alt_text,
                sort_order=sort_order,
                set_as_cover=set_as_cover,
            )
        ).model_dump()
    except VenueNotFoundError:
        return _venue_not_found()
    except FileTooLargeError:
        return error_response(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            code="file_too_large",
            message="Venue photo upload is too large.",
            details={"field": "file"},
        )
    except StorageNotConfiguredError:
        return error_response(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            code="storage_not_configured",
            message="R2 storage is not configured.",
            details={"provider": "cloudflare_r2"},
        )
    except StorageUploadError:
        return _storage_upload_failed()


@router.post("/venues/{venue_id}/photos/{photo_id}/cover")
async def set_venue_cover_photo(venue_id: int, photo_id: int, session: DbSession) -> dict:
    """Choose which photo represents the venue on the public listing."""
    try:
        return (await venue_service.set_cover_photo(session, venue_id, photo_id)).model_dump()
    except VenueNotFoundError:
        return _venue_not_found()


@router.delete("/venues/{venue_id}/photos/{photo_id}")
async def delete_venue_photo(venue_id: int, photo_id: int, session: DbSession) -> dict:
    try:
        return (await venue_service.delete_photo(session, venue_id, photo_id)).model_dump()
    except VenueNotFoundError:
        return _venue_not_found()


@router.post(
    "/articles/{article_id}/images",
    status_code=status.HTTP_201_CREATED,
    response_model=None,
)
async def upload_article_image(
    article_id: int,
    session: DbSession,
    file: UploadFile = File(...),
) -> dict | JSONResponse:
    """Store an inline image for an article body and return the URL the editor
    inserts. Variants are generated exactly as for venue photos, so the largest
    is used inline and the responsive set is available for later use."""
    try:
        await article_service.admin_detail(session, article_id)
    except ArticleNotFoundError:
        return _article_not_found()

    try:
        result = await venue_photo_storage.upload_article_image(
            file=file, article_id=article_id
        )
    except FileTooLargeError:
        return error_response(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            code="file_too_large",
            message="Article image upload is too large.",
            details={"field": "file"},
        )
    except StorageNotConfiguredError:
        return error_response(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            code="storage_not_configured",
            message="R2 storage is not configured.",
            details={"provider": "cloudflare_r2"},
        )
    except StorageUploadError as exc:
        return error_response(
            status_code=status.HTTP_502_BAD_GATEWAY,
            code="storage_upload_failed",
            message=str(exc),
            details={"provider": "cloudflare_r2"},
        )

    image = ArticleImage(
        article_id=article_id,
        filename=result.get("filename"),
        file_type=(result.get("content_type") or "").split("/")[-1] or None,
        file_size=result.get("file_size"),
        width=result.get("original_width"),
        height=result.get("original_height"),
        image=result.get("storage_key"),
        cdn_url=result.get("url"),
    )
    session.add(image)
    await session.commit()

    # Quill inserts this straight into the body.
    return {"url": result.get("url"), "thumbnail_url": result.get("thumbnail_url")}


@router.post("/uploads/venue-photo", status_code=status.HTTP_201_CREATED)
async def upload_temp_venue_photo(
    session: DbSession,
    file: UploadFile = File(...),
    temp_venue_id: str | None = Form(default=None),
    alt_text: str | None = Form(default=None),
    sort_order: int = Form(default=0),
) -> dict:
    if not _is_image_upload(file):
        return error_response(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            code="unsupported_file_type",
            message="Venue photos must be image uploads.",
            details={"field": "file"},
        )

    temp_id = temp_venue_id or str(uuid.uuid4())
    try:
        storage_result = await venue_photo_storage.upload(
            file=file,
            venue_id=None,
            temp_venue_id=temp_id,
        )
        photo = await venue_service.attach_temp_photo(
            session,
            temp_venue_id=temp_id,
            storage_result=storage_result,
            alt_text=alt_text,
            sort_order=sort_order,
        )
        return {**photo.model_dump(), "temp_venue_id": temp_id}
    except FileTooLargeError:
        return error_response(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            code="file_too_large",
            message="Venue photo upload is too large.",
            details={"field": "file"},
        )
    except StorageNotConfiguredError:
        return error_response(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            code="storage_not_configured",
            message="R2 storage is not configured.",
            details={"provider": "cloudflare_r2"},
        )
    except StorageUploadError:
        return _storage_upload_failed()


def _article_not_found() -> JSONResponse:
    return error_response(
        status_code=status.HTTP_404_NOT_FOUND,
        code="not_found",
        message="Article not found.",
        details={"resource": "article"},
    )


@router.get("/articles", response_model=ArticleAdminListResponse)
async def articles(session: DbSession) -> ArticleAdminListResponse:
    return ArticleAdminListResponse(items=await article_service.admin_list(session))


@router.get("/articles/{article_id}", response_model=None)
async def article_detail(article_id: int, session: DbSession) -> ArticleAdminDetail | JSONResponse:
    try:
        return await article_service.admin_detail(session, article_id)
    except ArticleNotFoundError:
        return _article_not_found()


@router.patch("/articles/{article_id}", response_model=None)
async def update_article(
    article_id: int, payload: ArticleUpdate, session: DbSession
) -> ArticleAdminDetail | JSONResponse:
    try:
        return await article_service.update(session, article_id, payload)
    except ArticleNotFoundError:
        return _article_not_found()
    except ArticleSlugConflictError as exc:
        return error_response(
            status_code=status.HTTP_409_CONFLICT,
            code="slug_conflict",
            message=str(exc),
            details={"field": "slug"},
        )


@router.delete("/articles/{article_id}", response_model=None)
async def delete_article(article_id: int, session: DbSession) -> dict | JSONResponse:
    try:
        await article_service.trash(session, article_id)
    except ArticleNotFoundError:
        return _article_not_found()
    return {"status": "deleted"}


@router.post("/articles", status_code=status.HTTP_201_CREATED, response_model=None)
async def create_article(
    payload: ArticleCreate,
    session: DbSession,
    current_user: Annotated[AuthenticatedUser, Depends(require_admin_user)],
) -> ArticleAdminDetail | JSONResponse:
    try:
        return await article_service.create(session, payload, author_id=current_user.id)
    except ArticleSlugConflictError as exc:
        return error_response(
            status_code=status.HTTP_409_CONFLICT,
            code="slug_conflict",
            message=str(exc),
            details={"field": "slug"},
        )


def _is_image_upload(file: UploadFile) -> bool:
    return (file.content_type or "").casefold().startswith("image/")


@router.get("/promotion-popup", response_model=PromotionPopupAdmin)
async def get_promotion_popup(session: DbSession) -> PromotionPopupAdmin:
    return await promotion_service.admin_detail(session)


@router.put("/promotion-popup", response_model=PromotionPopupAdmin)
async def update_promotion_popup(
    session: DbSession, payload: PromotionPopupUpdate
) -> PromotionPopupAdmin:
    detail = await promotion_service.update(session, payload)
    await session.commit()
    return detail


@router.post("/uploads/promotion-banner", status_code=status.HTTP_201_CREATED)
async def upload_promotion_banner(file: UploadFile = File(...)) -> dict:
    """Uploads the popup banner to R2 under packages/."""
    if not _is_image_upload(file):
        return error_response(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            code="unsupported_file_type",
            message="The banner must be an image upload.",
            details={"field": "file"},
        )

    result = await venue_photo_storage.upload_image(file=file, prefix="packages")
    return {"url": result.get("url"), "storage_key": result.get("storage_key")}


# --- Wedding showcases -------------------------------------------------------


def _showcase_not_found() -> JSONResponse:
    return error_response(
        status_code=status.HTTP_404_NOT_FOUND,
        code="not_found",
        message="Showcase not found.",
        details={"resource": "showcase"},
    )


def _showcase_slug_conflict(exc: Exception) -> JSONResponse:
    return error_response(
        status_code=status.HTTP_409_CONFLICT,
        code="slug_conflict",
        message=str(exc),
        details={"field": "slug"},
    )


@router.get("/showcases", response_model=ShowcaseAdminListResponse)
async def showcases(session: DbSession) -> ShowcaseAdminListResponse:
    return ShowcaseAdminListResponse(items=await showcase_service.admin_list(session))


@router.get("/showcases/{showcase_id}", response_model=None)
async def showcase_detail(
    showcase_id: int, session: DbSession
) -> ShowcaseAdminDetail | JSONResponse:
    try:
        return await showcase_service.admin_detail(session, showcase_id)
    except ShowcaseNotFoundError:
        return _showcase_not_found()


@router.post("/showcases", status_code=status.HTTP_201_CREATED, response_model=None)
async def create_showcase(
    payload: ShowcaseCreate, session: DbSession
) -> ShowcaseAdminDetail | JSONResponse:
    try:
        return await showcase_service.create(session, payload)
    except ShowcaseSlugConflictError as exc:
        return _showcase_slug_conflict(exc)


@router.patch("/showcases/{showcase_id}", response_model=None)
async def update_showcase(
    showcase_id: int, payload: ShowcaseUpdate, session: DbSession
) -> ShowcaseAdminDetail | JSONResponse:
    try:
        return await showcase_service.update(session, showcase_id, payload)
    except ShowcaseNotFoundError:
        return _showcase_not_found()
    except ShowcaseSlugConflictError as exc:
        return _showcase_slug_conflict(exc)


@router.delete("/showcases/{showcase_id}", response_model=None)
async def delete_showcase(showcase_id: int, session: DbSession) -> dict | JSONResponse:
    """Deletes the row, then its images and every generated variant from R2.

    The R2 sweep is best-effort: the record is already gone, so failing the
    request here would tell the editor the delete did not happen when it did.
    Orphaned objects are logged instead.
    """
    try:
        keys = await showcase_service.delete(session, showcase_id)
    except ShowcaseNotFoundError:
        return _showcase_not_found()

    removed = 0
    try:
        removed = await venue_photo_storage.delete_objects(keys)
    except StorageNotConfiguredError:
        pass
    except Exception as exc:  # noqa: BLE001 - never fail a completed delete
        logging.getLogger("app.storage").warning(
            "Showcase %s deleted but R2 cleanup failed: %s", showcase_id, exc
        )

    return {"status": "deleted", "images_removed": removed, "images_expected": len(keys)}


@router.post(
    "/uploads/showcase-image", status_code=status.HTTP_201_CREATED, response_model=None
)
async def upload_showcase_image(file: UploadFile = File(...)) -> dict | JSONResponse:
    """Uploads a showcase photo to R2 under showcases/, with responsive variants."""
    if not _is_image_upload(file):
        return error_response(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            code="unsupported_file_type",
            message="The showcase image must be an image upload.",
            details={"field": "file"},
        )

    try:
        result = await venue_photo_storage.upload_image(file=file, prefix="showcases")
    except FileTooLargeError:
        return error_response(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            code="file_too_large",
            message="The showcase image is too large.",
            details={"field": "file"},
        )
    except StorageNotConfiguredError:
        return error_response(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            code="storage_not_configured",
            message="Object storage is not configured.",
            details={},
        )
    except StorageUploadError:
        return _storage_upload_failed()

    return {
        "url": result.get("url"),
        "storage_key": result.get("storage_key"),
        "variants": showcase_image_variants(result),
    }
