from __future__ import annotations

import logging
import re
import uuid
from io import BytesIO
from typing import Any

from anyio import to_thread
from fastapi import UploadFile

from app.core.config import Settings
from app.services.images import render_variants, srcset_from

_UPLOAD_READ_CHUNK_SIZE = 1024 * 1024


class StorageNotConfiguredError(RuntimeError):
    pass


class FileTooLargeError(RuntimeError):
    pass


class StorageUploadError(RuntimeError):
    """The object store rejected the upload (bad credentials, network, etc.)."""


class R2VenuePhotoStorage:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client: Any | None = None

    async def upload(
        self,
        *,
        file: UploadFile,
        venue_id: int | None,
        temp_venue_id: str | None,
    ) -> dict[str, Any]:
        prefix = (
            f"venues/{venue_id}" if venue_id is not None else f"venues/temp/{temp_venue_id}"
        )
        return await self.upload_image(file=file, prefix=prefix)

    async def upload_article_image(
        self, *, file: UploadFile, article_id: int | None
    ) -> dict[str, Any]:
        """Inline images for article bodies. Same resizing and R2 layout as venue
        photos, so an article image is served responsively too."""
        prefix = f"articles/{article_id}" if article_id is not None else "articles/temp"
        return await self.upload_image(file=file, prefix=prefix)

    async def upload_image(self, *, file: UploadFile, prefix: str) -> dict[str, Any]:
        self._ensure_configured()

        contents = bytearray()
        while chunk := await file.read(_UPLOAD_READ_CHUNK_SIZE):
            contents.extend(chunk)
            if len(contents) > self._settings.venue_upload_max_bytes:
                raise FileTooLargeError("Venue photo upload is too large.")

        file_size = len(contents)
        original_filename = file.filename or "venue-photo"
        filename = safe_filename(original_filename)
        content_type = file.content_type or "application/octet-stream"
        storage_key = f"{prefix}/{uuid.uuid4().hex}-{filename}"

        try:
            await to_thread.run_sync(
                self._upload_bytes,
                bytes(contents),
                storage_key,
                content_type,
            )
        except (StorageNotConfiguredError, FileTooLargeError):
            raise
        except Exception as exc:  # boto3 / botocore client errors
            logging.getLogger("app.storage").warning("R2 upload failed: %s", exc)
            raise StorageUploadError(str(exc)) from exc

        base = self._settings.r2_public_base_url.rstrip("/")
        url = f"{base}/{storage_key}"

        result: dict[str, Any] = {
            "filename": filename,
            "original_filename": original_filename,
            "content_type": content_type,
            "file_size": file_size,
            "storage_key": storage_key,
            "url": url,
            "thumbnail_url": url,
            "variants": {"original": url},
        }

        rendered = await to_thread.run_sync(render_variants, bytes(contents))
        if rendered is None:
            # Not a decodable image (e.g. an odd format). The original is
            # already stored, so keep the upload rather than failing it.
            return result

        variants, metadata = rendered
        # Variant keys sit beside the original: <stem>_<label>_<width>w.<ext>
        stem = storage_key.rsplit(".", 1)[0]

        webp_entries: list[dict[str, Any]] = []
        jpeg_entries: list[dict[str, Any]] = []

        for variant in variants:
            variant_key = f"{stem}{variant.key_suffix}"
            try:
                await to_thread.run_sync(
                    self._upload_bytes, variant.content, variant_key, variant.content_type
                )
            except Exception as exc:  # one bad variant must not lose the upload
                logging.getLogger("app.storage").warning(
                    "R2 variant upload failed for %s: %s", variant_key, exc
                )
                continue

            entry = {
                "key": variant_key,
                "width": variant.width,
                "height": variant.height,
                "format": variant.fmt,
                "quality": variant.quality,
                "variant_type": variant.variant_type,
                "file_size": len(variant.content),
                "filename": variant_key.rsplit("/", 1)[-1],
                "cdn_url": f"{base}/{variant_key}",
                "s3_url": f"{base}/{variant_key}",
                "orientation": metadata["orientation"],
                "success": True,
            }
            (webp_entries if variant.fmt == "webp" else jpeg_entries).append(entry)

        if not webp_entries and not jpeg_entries:
            return result

        # Point the single-URL fields at real sizes: the smallest jpeg for a
        # thumbnail, the largest for the detail view.
        if jpeg_entries:
            result["thumbnail_url"] = jpeg_entries[0]["cdn_url"]
            result["url"] = jpeg_entries[-1]["cdn_url"]

        result.update(
            {
                "webp_variants": webp_entries,
                "jpeg_variants": jpeg_entries,
                "webp_srcset": srcset_from(webp_entries),
                "jpeg_srcset": srcset_from(jpeg_entries),
                "sizes_attribute": metadata["sizes_attribute"],
                "breakpoints_used": metadata["breakpoints_used"],
                "formats_generated": ["webp", "jpeg"],
                "original_width": metadata["original_width"],
                "original_height": metadata["original_height"],
                "orientation": metadata["orientation"],
                "variants": {"original": url},
            }
        )
        return result

    def _ensure_configured(self) -> None:
        required = [
            self._settings.r2_endpoint_url,
            self._settings.r2_access_key_id,
            self._settings.r2_secret_access_key,
            self._settings.r2_bucket_name,
            self._settings.r2_public_base_url,
        ]
        if any(value is None or value == "" for value in required):
            raise StorageNotConfiguredError("R2 storage is not configured.")

    async def delete_objects(self, keys: list[str]) -> int:
        """Remove objects from R2. Returns how many the bucket accepted.

        Deliberately takes explicit keys rather than a prefix: variant keys are
        `<stem>_<label>_<width>w.<ext>`, and one showcase's stem can be a
        prefix of another's (`...-07-29` vs `...-07-29-2`), so a prefix sweep
        would delete a neighbouring record's images.
        """
        if not keys:
            return 0
        self._ensure_configured()
        return await to_thread.run_sync(self._delete_bytes_keys, keys)

    def _delete_bytes_keys(self, keys: list[str]) -> int:
        client = self._get_client()
        bucket = self._settings.r2_bucket_name
        deleted = 0
        # delete_objects caps at 1000 keys per call; a showcase has ~11.
        for start in range(0, len(keys), 1000):
            chunk = keys[start : start + 1000]
            response = client.delete_objects(
                Bucket=bucket,
                Delete={"Objects": [{"Key": key} for key in chunk], "Quiet": True},
            )
            for problem in response.get("Errors", []) or []:
                logging.getLogger("app.storage").warning(
                    "R2 delete failed for %s: %s", problem.get("Key"), problem.get("Message")
                )
            deleted += len(chunk) - len(response.get("Errors", []) or [])
        return deleted

    def _upload_bytes(self, contents: bytes, storage_key: str, content_type: str) -> None:
        self._get_client().upload_fileobj(
            BytesIO(contents),
            self._settings.r2_bucket_name,
            storage_key,
            ExtraArgs={"ContentType": content_type},
        )

    def _get_client(self) -> Any:
        if self._client is None:
            import boto3

            self._client = boto3.client(
                "s3",
                endpoint_url=self._settings.r2_endpoint_url,
                aws_access_key_id=self._settings.r2_access_key_id,
                aws_secret_access_key=self._settings.r2_secret_access_key,
                region_name="auto",
            )
        return self._client


def safe_filename(filename: str) -> str:
    name = filename.strip().lower()
    name = re.sub(r"[^a-z0-9._-]+", "-", name)
    name = re.sub(r"-+", "-", name).strip("-.")
    return name or "venue-photo"
