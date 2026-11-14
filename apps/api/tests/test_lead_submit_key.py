"""LEAD_SUBMIT_KEY: the lead endpoints accept only what the website forwards.

The captcha is checked on the website. Bots that posted straight to the API
skipped it, which is how spam kept arriving after the captcha shipped.
"""

from __future__ import annotations

import pytest

from app.core.config import Settings, get_settings
from app.main import app
from app.services.leads import lead_service

LEAD_ENDPOINTS = [
    "/api/v1/public/contact-leads",
    "/api/v1/public/venue-pricing-requests",
    "/api/v1/public/tool-leads",
    "/api/v1/public/tour/register",
    "/api/v1/public/tour/branches/jakarta/register",
]


class SilentNotifier:
    async def send_lead_notification(self, **kwargs) -> bool:
        return True

    async def send_lead_alert(self, **kwargs) -> bool:
        return True


@pytest.fixture()
def keyed(api, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(lead_service, "_notifier", SilentNotifier())
    monkeypatch.setattr(lead_service, "_whatsapp", SilentNotifier())
    app.dependency_overrides[get_settings] = lambda: Settings(lead_submit_key="site-secret")
    return api


@pytest.mark.parametrize("endpoint", LEAD_ENDPOINTS)
def test_a_lead_without_the_key_is_refused(keyed, endpoint: str) -> None:
    response = keyed.client.post(endpoint, json={})

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "website_access_denied"


@pytest.mark.parametrize("endpoint", LEAD_ENDPOINTS)
def test_a_lead_with_the_wrong_key_is_refused(keyed, endpoint: str) -> None:
    response = keyed.client.post(endpoint, json={}, headers={"x-7magic-lead-key": "guess"})

    assert response.status_code == 403


def test_a_lead_with_the_key_goes_through(keyed) -> None:
    response = keyed.client.post(
        "/api/v1/public/tool-leads",
        json={
            "tool": "mahar",
            "email": "andre@example.com",
            "phone": "+6281234567890",
            "consent": True,
            "website": "",
        },
        headers={"x-7magic-lead-key": "site-secret"},
    )

    assert response.status_code == 201


def test_without_a_configured_key_leads_are_unguarded(api) -> None:
    # Validation runs, so the request got past the guard.
    response = api.client.post("/api/v1/public/contact-leads", json={})

    assert response.status_code == 422
