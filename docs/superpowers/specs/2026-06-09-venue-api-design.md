# Venue API Design

Date: 2026-06-09

## Goal

Add model-backed venue API endpoints for the 7magic FastAPI app. The CMS must manage venues through protected `/api/v1/admin` routes, while the public website consumes active venue data through guarded `/api/v1/venues` routes. Venue image upload must store files in Cloudflare R2 and persist photo metadata.

## Current Context

The API already has SQLAlchemy models for `Venue`, `VenuePhoto`, and `MediaAsset`, plus a Cloudflare R2-oriented `R2VenuePhotoStorage` service. Existing `/api/v1/admin/venues` endpoints are implemented against the in-memory `CatalogService`, so venue model tables are not the source of truth for CMS CRUD or upload metadata. Existing public venue reads live under `/api/v1/public/venues` and are also backed by fixtures.

## Route Design

### CMS Admin Routes

Admin routes remain protected by `require_admin_user` and continue to use the `/api/v1/admin` prefix.

- `GET /api/v1/admin/venues` lists venues for CMS management.
- `POST /api/v1/admin/venues` creates a venue.
- `GET /api/v1/admin/venues/{venue_id}` returns full CMS venue detail.
- `PATCH /api/v1/admin/venues/{venue_id}` updates editable venue fields.
- `DELETE /api/v1/admin/venues/{venue_id}` archives by default instead of hard-deleting business data.
- `POST /api/v1/admin/venues/{venue_id}/photos` uploads a venue image to R2 and attaches it to the venue.
- `DELETE /api/v1/admin/venues/{venue_id}/photos/{photo_id}` removes a photo record from the venue. R2 object deletion can be added later when object lifecycle policy is agreed.

### Website Venue Routes

Website-facing routes use `/api/v1/venues`, not `/api/v1/public/venues`, so the SvelteKit website has a stable venue-specific API surface.

- `GET /api/v1/venues` returns active venues only, with capped pagination and optional filters such as `q`, `city`, and `stars_min`.
- `GET /api/v1/venues/{city}/{slug}` returns active venue detail only.

These responses must exclude draft or archived venues, storage keys, temporary upload identifiers, internal CMS-only metadata, and fields not needed by the website.

## Data Model Use

Venue CRUD uses `app.models.venue.Venue` as the source of truth. Photo upload and gallery responses use `VenuePhoto`.

The existing `VenueCreate`, `VenueUpdate`, `VenueDetail`, `VenueListResponse`, and `VenuePhotoResponse` schemas can be reused where their shape fits. Add separate admin and website response schemas only where the existing content schemas expose the wrong fields or force fixture-specific assumptions.

The unique business constraint is `city + slug`. Create and update operations return a `409 slug_conflict` error when that pair is already used by another venue.

## R2 Upload Flow

`POST /api/v1/admin/venues/{venue_id}/photos` accepts multipart form data:

- `file`: required image upload.
- `alt_text`: optional string.
- `sort_order`: optional integer, default `0`.
- `set_as_cover`: optional boolean.

Validation:

- Reject non-image uploads with `422 unsupported_file_type`.
- Enforce a configured maximum file size before uploading.
- Sanitize filenames before building storage keys.
- Return `404 not_found` if the venue does not exist.
- Return `503 storage_not_configured` if R2 settings are missing.

Storage key format:

```text
venues/{venue_id}/{uuid}-{safe_filename}
```

The upload stores the original object in R2, builds the public CDN URL from `r2_public_base_url`, and persists photo metadata in `venue_photos`. Generated image variants are out of scope unless already provided by the storage service.

## Website Scraping Controls

Browser-consumable data cannot be made impossible to scrape, so the API should reduce casual scraping and abusive bulk collection:

- Cap `page_size` to a small maximum.
- Return narrow venue fields on list routes.
- Serve only `status = active` venues.
- Add a website-read dependency for `/api/v1/venues` that can enforce allowed `Origin`/`Referer` values and an optional public read key header.
- Add lightweight rate limiting by client identity when the project has a shared cache or middleware slot available.

The first implementation should include the route dependency and config hooks even if rate limiting starts as a simple in-process guard, so it can later move to Redis or edge protection without changing route handlers.

## Error Handling

Use the existing `error_response` envelope:

```json
{
  "error": {
    "code": "not_found",
    "message": "Venue not found.",
    "details": {"resource": "venue"}
  }
}
```

Expected venue errors:

- `404 not_found` for missing venues or photos.
- `409 slug_conflict` for duplicate `city + slug`.
- `422 unsupported_file_type` for non-image uploads.
- `413 file_too_large` for oversized uploads.
- `503 storage_not_configured` for missing R2 config.
- `403 website_access_denied` for website-read guard failures.
- `429 rate_limited` for abusive website-read traffic.

## Testing

Add API tests that use a temporary SQLite database and dependency overrides, following the auth contract tests.

Required coverage:

- Admin venue CRUD uses database state.
- Admin routes still require bearer admin auth.
- Duplicate `city + slug` is rejected.
- Delete archives a venue and removes it from website responses.
- Website list/detail only return active venues.
- Website route guard rejects disallowed access when configured.
- R2 upload validates image content type, handles missing storage config, and persists photo metadata when storage is mocked.

## Open Decisions

- Whether `DELETE /admin/venues/{venue_id}` should ever hard-delete, or only archive.
- Whether R2 object deletion should happen when a photo is removed.
- Whether the website-read key should be required in all environments or only production-like environments.
