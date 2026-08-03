from functools import lru_cache

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "7magic API"
    app_version: str = "0.0.0"
    api_v1_prefix: str = "/api/v1"
    database_url: str = "sqlite+aiosqlite:///./7magic.db"
    session_ttl_seconds: int = 60 * 60 * 24 * 14
    # Hard cap on total session age; sliding refresh never extends past this.
    session_max_lifetime_seconds: int = 60 * 60 * 24 * 30
    login_max_attempts: int = 5
    login_window_seconds: int = 900
    # Object storage (Cloudflare R2 / S3-compatible). Accept the legacy R2_*
    # names as well as the AWS_*/OBJECT_STORAGE_* names used in .env.
    r2_endpoint_url: str | None = Field(
        default=None,
        validation_alias=AliasChoices("r2_endpoint_url", "R2_ENDPOINT_URL", "AWS_ENDPOINT_URL"),
    )
    r2_access_key_id: str | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "r2_access_key_id", "R2_ACCESS_KEY_ID", "AWS_ACCESS_KEY_ID"
        ),
    )
    r2_secret_access_key: str | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "r2_secret_access_key", "R2_SECRET_ACCESS_KEY", "AWS_SECRET_ACCESS_KEY"
        ),
    )
    r2_bucket_name: str | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "r2_bucket_name", "R2_BUCKET_NAME", "OBJECT_STORAGE_BUCKET"
        ),
    )
    r2_public_base_url: str | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "r2_public_base_url", "R2_PUBLIC_BASE_URL", "OBJECT_STORAGE_PUBLIC_BASE_URL"
        ),
    )

    # Transactional email (Resend). Leads are always persisted; email is a
    # notification on top, so an unset key degrades to a logged warning
    # rather than a failed submission.
    resend_api_key: str | None = Field(
        default=None,
        validation_alias=AliasChoices("resend_api_key", "RESEND_API_KEY"),
    )
    lead_notification_email: str = Field(
        default="info@7magicwedding.com",
        validation_alias=AliasChoices("lead_notification_email", "LEAD_NOTIFICATION_EMAIL"),
    )
    lead_notification_from: str = Field(
        default="7Magic Website <onboarding@resend.dev>",
        validation_alias=AliasChoices("lead_notification_from", "LEAD_NOTIFICATION_FROM"),
    )

    # WhatsApp via Bird (formerly MessageBird). Bird carries WhatsApp only --
    # transactional email stays on Resend above. Every field is optional so the
    # API boots unconfigured: sends degrade to a logged warning, exactly like
    # Resend, and the inbound webhook refuses everything while the signing key
    # is unset rather than trusting unverified payloads.
    # The bk_-prefixed key from Bird's developer API. Both env names are
    # accepted: Bird's dashboard calls it an access key, its SDKs an api_key.
    bird_api_key: str | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "bird_api_key", "BIRD_API_KEY", "BIRD_ACCESS_KEY"
        ),
    )
    # ws_-prefixed, not the UUID the older Channels API docs describe.
    bird_workspace_id: str | None = Field(
        default=None,
        validation_alias=AliasChoices("bird_workspace_id", "BIRD_WORKSPACE_ID"),
    )
    # Only exists once a WhatsApp channel is created, which needs the WABA. The
    # send path must tolerate it being unset until then.
    bird_whatsapp_channel_id: str | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "bird_whatsapp_channel_id", "BIRD_WHATSAPP_CHANNEL_ID"
        ),
    )
    # Normally derived from the key's region segment; set only to point at a
    # stub or a region the key does not encode.
    bird_base_url: str | None = Field(
        default=None,
        validation_alias=AliasChoices("bird_base_url", "BIRD_BASE_URL"),
    )
    # An approved `utility` template with four body slots: name, contact, page,
    # message. Bird accepts nothing but templates, so this name must match one
    # approved in the dashboard or every alert is rejected.
    bird_lead_template: str = Field(
        default="lead_alert",
        validation_alias=AliasChoices("bird_lead_template", "BIRD_LEAD_TEMPLATE"),
    )
    bird_lead_template_language: str = Field(
        default="id",
        validation_alias=AliasChoices(
            "bird_lead_template_language", "BIRD_LEAD_TEMPLATE_LANGUAGE"
        ),
    )
    # How many body slots that template has. A send whose parameter count does
    # not match is rejected, so this exists to borrow one of Bird's system
    # templates (which have fewer) until a purpose-built one is approved.
    bird_lead_template_slots: int = Field(
        default=4,
        ge=1,
        validation_alias=AliasChoices(
            "bird_lead_template_slots", "BIRD_LEAD_TEMPLATE_SLOTS"
        ),
    )
    # Signs the inbound webhook; unrelated to the API key used for sending.
    bird_webhook_signing_key: str | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "bird_webhook_signing_key", "BIRD_WEBHOOK_SIGNING_KEY"
        ),
    )
    # Where new-lead alerts are sent, in E.164. Not the WABA number itself --
    # a channel cannot message itself.
    whatsapp_team_number: str | None = Field(
        default=None,
        validation_alias=AliasChoices("whatsapp_team_number", "WHATSAPP_TEAM_NUMBER"),
    )

    venue_read_allowed_origins: list[str] = []
    venue_read_api_key: str | None = None
    venue_upload_max_bytes: int = 10 * 1024 * 1024
    # The https names are what Caddy serves in dev; the raw ports stay for
    # running an app directly with `vite dev`, bypassing the proxy.
    cors_origins: list[str] = [
        "https://7magic.localhost",
        "https://cms.7magic.localhost",
        "http://localhost:5180",
        "http://127.0.0.1:5180",
        "http://localhost:5181",
        "http://127.0.0.1:5181",
        "http://localhost:5182",
        "http://127.0.0.1:5182",
    ]

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", populate_by_name=True)


@lru_cache
def get_settings() -> Settings:
    return Settings()
