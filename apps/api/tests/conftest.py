"""Test-wide isolation from the notification providers.

pydantic-settings reads `apps/api/.env`, which on a developer machine holds real
Bird and Resend credentials. The lead tests exercise the full submit path, so
without this module a plain `uv run pytest` would post live WhatsApp alerts to
the team's phone -- and bill for them -- on every run.

Blanking the keys in the environment beats the dotenv file, because environment
variables take precedence there. It has to happen at import time: pytest imports
conftest before any test module, and `app.services.leads` builds its notifiers
from `get_settings()` at import. The cache clear covers the case where something
has already read the settings.
"""

import os

from app.core.config import get_settings

# Every credential that could cause an outbound call during a test run.
for _name in (
    "BIRD_API_KEY",
    "BIRD_ACCESS_KEY",
    "BIRD_BASE_URL",
    "BIRD_WEBHOOK_SIGNING_KEY",
    "WHATSAPP_TEAM_NUMBER",
    "RESEND_API_KEY",
):
    os.environ[_name] = ""

get_settings.cache_clear()
