from sqlalchemy import CheckConstraint, UniqueConstraint

from app.core.database import Base
from app.models import (
    Article,
    ArticleCategory,
    ArticleImage,
    AuditEvent,
    ContactLead,
    MediaAsset,
    Role,
    User,
    UserRole,
    UserSession,
    Venue,
    VenuePhoto,
)


def test_core_tables_are_registered_for_migrations() -> None:
    table_names = set(Base.metadata.tables)

    assert {
        "articles",
        "article_categories",
        "article_images",
        "audit_events",
        "contact_leads",
        "media_assets",
        "roles",
        "sessions",
        "user_roles",
        "users",
        "venue_photos",
        "venues",
    }.issubset(table_names)


def test_venue_model_has_public_slug_and_photo_relationship() -> None:
    venue_constraints = Venue.__table__.constraints
    unique_constraints = [
        constraint for constraint in venue_constraints if isinstance(constraint, UniqueConstraint)
    ]

    assert Venue.__tablename__ == "venues"
    assert Venue.path_for(city="Jakarta", slug="grand-ballroom") == (
        "/wedding-venue/jakarta/grand-ballroom"
    )
    assert any({"city", "slug"} == {column.name for column in constraint.columns} for constraint in unique_constraints)
    assert VenuePhoto.__table__.c.venue_id.foreign_keys


def test_article_model_tracks_status_slug_and_author_relationships() -> None:
    article_constraints = Article.__table__.constraints
    check_constraints = [
        constraint for constraint in article_constraints if isinstance(constraint, CheckConstraint)
    ]
    unique_constraints = [
        constraint for constraint in article_constraints if isinstance(constraint, UniqueConstraint)
    ]

    assert Article.__tablename__ == "articles"
    assert ArticleCategory.__tablename__ == "article_categories"
    assert ArticleImage.__table__.c.article_id.foreign_keys
    assert any("status" in str(constraint.sqltext) for constraint in check_constraints)
    assert any(
        {"category_id", "slug"} == {column.name for column in constraint.columns}
        for constraint in unique_constraints
    )


def test_user_role_auth_and_operational_models_exist() -> None:
    assert User.__table__.c.email.unique is True
    assert Role.__table__.c.name.unique is True
    assert UserRole.__table__.c.user_id.foreign_keys
    assert UserSession.__table__.c.user_id.foreign_keys
    assert UserSession.__table__.c.token_hash.unique is True
    assert MediaAsset.__table__.c.owner_type.nullable is False
    assert AuditEvent.__table__.c.actor_id.foreign_keys
    assert ContactLead.__table__.c.source.nullable is False


def test_event_registration_records_an_uncatalogued_venue() -> None:
    """The network is wider than the published venue table, so a tour can be booked
    at a venue with no row here. The typed name and the city are what the team gets
    in that case, and the city is also what routes the lead to a branch."""
    from app.domains.events.models import EventRegistration

    columns = EventRegistration.__table__.columns

    assert columns["venue_name"].nullable is True
    assert columns["venue_name"].type.length == 300
    assert columns["city"].nullable is True
    assert columns["city"].type.length == 80
