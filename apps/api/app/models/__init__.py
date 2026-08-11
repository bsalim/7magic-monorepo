# Domain-package models are re-exported here so `import app.models` still answers
# "what tables exist" -- alembic's env.py and the test fixtures both rely on that.
from app.domains.branches.models import Branch, BranchClosure, BranchOpeningHour, BranchSettings
from app.domains.events.models import (
    Event,
    EventEmailTemplate,
    EventRegistration,
    EventRegistrationGuest,
)
from app.models.article import Article, ArticleCategory, ArticleImage, ArticleTag
from app.models.audit import AuditEvent, ContactLead
from app.models.media import MediaAsset
from app.models.promotion import PromotionPopup
from app.models.session import UserSession
from app.models.showcase import Showcase
from app.models.translation import VenueTranslation
from app.models.user import Role, User, UserRole
from app.models.venue import Venue, VenuePhoto

__all__ = [
    "Article",
    "ArticleCategory",
    "ArticleImage",
    "ArticleTag",
    "AuditEvent",
    "Branch",
    "BranchClosure",
    "BranchOpeningHour",
    "BranchSettings",
    "ContactLead",
    "Event",
    "EventEmailTemplate",
    "EventRegistration",
    "EventRegistrationGuest",
    "MediaAsset",
    "PromotionPopup",
    "Role",
    "Showcase",
    "User",
    "UserRole",
    "UserSession",
    "Venue",
    "VenuePhoto",
    "VenueTranslation",
]
