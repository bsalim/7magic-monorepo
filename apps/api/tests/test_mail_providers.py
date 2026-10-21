"""Mail provider selection, and the two provider payloads.

Every other test in the suite monkeypatches `send_email` away, so without this
file the whole transport layer ships unexercised: which provider is chosen, what
each puts on the wire, and the best-effort contracts the callers depend on.

Resend is a flat JSON POST; SES is a boto3 call with a nested request, its own
credentials, and an endpoint that has to be pinned because the process
environment's AWS_ENDPOINT_URL points at R2. The SES tests that earn their place
pin exactly those differences.

No test here reaches the network: Resend is built with a recording transport,
SES with a botocore Stubber.
"""

from __future__ import annotations

import json
from typing import Any

import boto3
import httpx
import pytest
from botocore.exceptions import ClientError, EndpointConnectionError
from botocore.stub import Stubber
from pydantic import ValidationError

from app.core.config import Settings
from app.services.email.base import EmailMessage
from app.services.email.bird import BirdMailer
from app.services.email.resend import RESEND_ENDPOINT, ResendMailer
from app.services.email.ses import SesMailer, ses_endpoint
from app.services.email.service import EmailNotifier, get_mailer


def make_settings(**overrides: Any) -> Settings:
    """Every mail field is pinned, including ones a given test does not assert
    on. Settings falls through to apps/api/.env for anything left unset, so
    omitting one silently couples the suite to whatever a developer happens to
    have configured -- which is how a local BIRD_LEAD_TEMPLATE_SLOTS once turned
    four assertions in test_whatsapp_notifier red."""
    base: dict[str, Any] = {
        "mail_provider": "resend",
        "resend_api_key": "re_testkey",
        "ses_access_key_id": "AKIATESTKEY",
        "ses_secret_access_key": "test-secret",
        "ses_region": "ap-southeast-1",
        "ses_configuration_set": None,
        "bird_mail_api_key": "bk_us1_testtoken",
        "bird_mail_category": "transactional",
        "bird_base_url": None,
        "lead_notification_from": "7Magic <hello@7magicwedding.com>",
        "lead_notification_email": "info@7magicwedding.com",
        "admin_emails": "",
        "email_logo_url": "",
    }
    base.update(overrides)
    return Settings(**base)


class RecordingTransport(httpx.AsyncBaseTransport):
    """Captures the request instead of reaching the provider."""

    def __init__(self, status_code: int = 202, error: Exception | None = None) -> None:
        self.status_code = status_code
        self.error = error
        self.request: httpx.Request | None = None

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        self.request = request
        if self.error is not None:
            raise self.error
        return httpx.Response(self.status_code, json={"id": "em_1", "status": "accepted"})


def sent(transport: RecordingTransport) -> dict[str, Any]:
    assert transport.request is not None
    return json.loads(transport.request.content)


class StubbedSes:
    """A real sesv2 client with botocore's Stubber in front of it, so the request
    is validated against the actual SES model -- a misspelt key fails here, not
    in production -- and never leaves the process."""

    def __init__(self, error_code: str | None = None) -> None:
        self.client = boto3.client(
            "sesv2",
            region_name="ap-southeast-1",
            aws_access_key_id="x",
            aws_secret_access_key="x",
        )
        self.stubber = Stubber(self.client)
        self.error_code = error_code
        self.request: dict[str, Any] | None = None

    def expect(self, request: dict[str, Any] | None = None) -> None:
        """Queue one send. With no request given, any parameters are accepted and
        captured for the test to assert on."""
        if self.error_code:
            self.stubber.add_client_error(
                "send_email", service_error_code=self.error_code, http_status_code=400
            )
        else:
            self.stubber.add_response("send_email", {"MessageId": "m_1"}, request)
        self.stubber.activate()
        self.client.meta.events.register("provide-client-params.sesv2.SendEmail", self._capture)

    def _capture(self, params: dict[str, Any], **_: Any) -> None:
        self.request = params


class UnreachableSes:
    def send_email(self, **_: Any) -> None:
        raise EndpointConnectionError(endpoint_url="https://email.example.test")


def ses(stub: StubbedSes, **overrides: Any) -> SesMailer:
    stub.expect()
    return SesMailer(make_settings(mail_provider="ses", **overrides), client=stub.client)


MESSAGE = EmailMessage(to=["dina@example.test"], subject="Hi", text="Hello")


# --- Provider selection -------------------------------------------------------


def test_resend_is_the_default_provider() -> None:
    assert isinstance(get_mailer(make_settings()), ResendMailer)


def test_ses_is_selected_by_config() -> None:
    assert isinstance(get_mailer(make_settings(mail_provider="ses")), SesMailer)


def test_bird_is_selected_by_config() -> None:
    """Bird stays selectable beside SES, so switching is one variable and a
    restart in either direction."""
    assert isinstance(get_mailer(make_settings(mail_provider="bird")), BirdMailer)


def test_an_unknown_provider_fails_at_settings_construction() -> None:
    """A typo must fail at boot, not degrade to silently sending nothing."""
    with pytest.raises(ValidationError):
        make_settings(mail_provider="sendgrid")


# --- SES on the wire ----------------------------------------------------------


def test_ses_pins_its_endpoint_and_credentials(monkeypatch) -> None:
    """systemd loads the env file into the environment, where AWS_ENDPOINT_URL,
    AWS_ACCESS_KEY_ID and AWS_REGION are all R2's. boto3 honours every one of
    them, so the client must be built from the SES settings alone."""
    monkeypatch.setenv("AWS_ENDPOINT_URL", "https://r2.example.test")
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "r2-key")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "r2-secret")
    monkeypatch.setenv("AWS_REGION", "auto")

    client = SesMailer(make_settings(mail_provider="ses"))._get_client()

    assert client.meta.endpoint_url == ses_endpoint("ap-southeast-1")
    assert client.meta.region_name == "ap-southeast-1"
    assert client._request_signer._credentials.access_key == "AKIATESTKEY"


@pytest.mark.asyncio
async def test_ses_sends_a_well_formed_request() -> None:
    """The exact shape, validated by the Stubber against the real SES model."""
    stub = StubbedSes()
    stub.expect(
        {
            "FromEmailAddress": "7Magic <hello@7magicwedding.com>",
            "Destination": {"ToAddresses": ["one@example.test", "two@example.test"]},
            "ReplyToAddresses": ["team@7magic.test"],
            "Content": {
                "Simple": {
                    "Subject": {"Data": "Hi", "Charset": "UTF-8"},
                    "Body": {
                        "Text": {"Data": "Plain", "Charset": "UTF-8"},
                        "Html": {"Data": "<p>Rich</p>", "Charset": "UTF-8"},
                    },
                }
            },
        }
    )
    mailer = SesMailer(make_settings(mail_provider="ses"), client=stub.client)

    await mailer.send(
        EmailMessage(
            to=["one@example.test", "two@example.test"],
            subject="Hi",
            text="Plain",
            html="<p>Rich</p>",
            reply_to="team@7magic.test",
        )
    )

    stub.stubber.assert_no_pending_responses()


@pytest.mark.asyncio
async def test_ses_omits_html_and_reply_to_when_there_are_none() -> None:
    stub = StubbedSes()

    await ses(stub).send(MESSAGE)

    assert stub.request is not None
    assert "Html" not in stub.request["Content"]["Simple"]["Body"]
    assert "ReplyToAddresses" not in stub.request
    assert "ConfigurationSetName" not in stub.request


@pytest.mark.asyncio
async def test_ses_names_the_configuration_set_when_one_is_set() -> None:
    stub = StubbedSes()

    await ses(stub, ses_configuration_set="7magic-transactional").send(MESSAGE)

    assert stub.request is not None
    assert stub.request["ConfigurationSetName"] == "7magic-transactional"


@pytest.mark.asyncio
async def test_ses_raises_on_a_rejected_send() -> None:
    """Raising is the contract; each caller decides what to do about it."""
    stub = StubbedSes(error_code="MessageRejected")

    with pytest.raises(ClientError):
        await ses(stub).send(MESSAGE)


# --- Resend on the wire -------------------------------------------------------


@pytest.mark.asyncio
async def test_resend_posts_to_its_own_endpoint() -> None:
    transport = RecordingTransport(status_code=200)

    await ResendMailer(make_settings(), transport=transport).send(MESSAGE)

    assert transport.request is not None
    assert str(transport.request.url) == RESEND_ENDPOINT
    assert transport.request.headers["Authorization"] == "Bearer re_testkey"


@pytest.mark.asyncio
async def test_resend_takes_a_scalar_reply_to() -> None:
    """Where SES takes a list."""
    transport = RecordingTransport(status_code=200)

    await ResendMailer(make_settings(), transport=transport).send(
        EmailMessage(to=["a@b.test"], subject="Hi", text="Hello", reply_to="team@7magic.test")
    )

    assert sent(transport)["reply_to"] == "team@7magic.test"


# --- Configured, or degrading quietly -----------------------------------------


@pytest.mark.parametrize("missing", ["ses_access_key_id", "ses_secret_access_key", "ses_region"])
def test_ses_is_unconfigured_without_any_one_of_its_settings(missing: str) -> None:
    """No region default either: identities are verified per region, so a guess
    would only move the failure from boot to every send."""
    assert not SesMailer(make_settings(**{missing: None})).configured


def test_ses_is_configured_with_all_three() -> None:
    assert SesMailer(make_settings()).configured


def test_resend_is_unconfigured_without_a_key() -> None:
    assert not ResendMailer(make_settings(resend_api_key=None)).configured


def test_ses_never_borrows_the_r2_credentials(monkeypatch) -> None:
    """AWS_ACCESS_KEY_ID is R2's in this app. Reading it as an SES fallback
    would sign mail requests with the bucket's key."""
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "r2-key")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "r2-secret")
    monkeypatch.setenv("AWS_REGION", "auto")

    settings = Settings(_env_file=None)

    # Falsy rather than None: conftest blanks the SES names to "".
    assert not settings.ses_access_key_id
    assert not settings.ses_secret_access_key
    assert not settings.ses_region


def test_the_suite_cannot_reach_a_live_mail_provider() -> None:
    """conftest blanks every provider credential so a test run cannot post live
    mail or bill for it. BIRD_MAIL_API_KEY was added to Settings without being
    added there, and a key exported in the environment beats the dotenv file --
    so this pins the whole list rather than just the one that was missed."""
    import os

    for name in (
        "BIRD_API_KEY",
        "BIRD_ACCESS_KEY",
        "BIRD_MAIL_API_KEY",
        "SES_ACCESS_KEY_ID",
        "SES_SECRET_ACCESS_KEY",
        "RESEND_API_KEY",
        "WHATSAPP_TEAM_NUMBER",
    ):
        assert os.environ.get(name) == "", f"{name} is not blanked for tests"

    live = Settings()
    assert not live.ses_access_key_id
    assert not live.bird_mail_api_key
    assert not live.resend_api_key
    # And so nothing is configured to send in the first place.
    assert not get_mailer(live).configured


# --- The contracts the callers depend on --------------------------------------


@pytest.mark.asyncio
async def test_a_lead_notification_returns_false_rather_than_raising() -> None:
    """leads.py treats False as "saved, not notified". It must never see an
    exception -- the lead row is already committed by the time this runs."""
    settings = make_settings()
    notifier = EmailNotifier(settings)
    notifier._mailer = ResendMailer(
        settings, transport=RecordingTransport(error=httpx.ConnectError("boom"))
    )

    result = await notifier.send_lead_notification(
        subject="New enquiry", heading="New contact enquiry", fields={"Name": "Dina"}
    )

    assert result is False


@pytest.mark.asyncio
async def test_a_rejected_lead_notification_returns_false() -> None:
    settings = make_settings()
    notifier = EmailNotifier(settings)
    notifier._mailer = ResendMailer(settings, transport=RecordingTransport(status_code=422))

    result = await notifier.send_lead_notification(
        subject="New enquiry", heading="New contact enquiry", fields={"Name": "Dina"}
    )

    assert result is False


@pytest.mark.asyncio
async def test_an_ses_rejection_returns_false_rather_than_raising() -> None:
    """SES fails with botocore's exceptions, not httpx's -- the notifier has to
    catch both families or an unverified sender becomes a 500 on the form."""
    settings = make_settings(mail_provider="ses")
    stub = StubbedSes(error_code="MessageRejected")
    notifier = EmailNotifier(settings)
    notifier._mailer = ses(stub)

    result = await notifier.send_lead_notification(
        subject="New enquiry", heading="New contact enquiry", fields={"Name": "Dina"}
    )

    assert result is False


@pytest.mark.asyncio
async def test_an_unreachable_ses_returns_false_rather_than_raising() -> None:
    settings = make_settings(mail_provider="ses")
    notifier = EmailNotifier(settings)
    notifier._mailer = SesMailer(settings, client=UnreachableSes())

    result = await notifier.send_lead_notification(
        subject="New enquiry", heading="New contact enquiry", fields={"Name": "Dina"}
    )

    assert result is False


@pytest.mark.asyncio
async def test_a_lead_notification_carries_html_and_a_text_alternative() -> None:
    transport = RecordingTransport()
    settings = make_settings()
    notifier = EmailNotifier(settings)
    notifier._mailer = ResendMailer(settings, transport=transport)

    assert await notifier.send_lead_notification(
        subject="New enquiry", heading="New contact enquiry", fields={"Name": "Dina"}
    )

    payload = sent(transport)
    assert "Dina" in payload["html"]
    assert "Dina" in payload["text"]
    assert payload["to"] == ["info@7magicwedding.com"]


@pytest.mark.asyncio
async def test_a_lead_notification_goes_to_every_admin_email() -> None:
    """ADMIN_EMAILS is typed by hand into an env file, so stray spaces, a trailing
    comma and the same address in another case all have to be survivable."""
    transport = RecordingTransport()
    settings = make_settings(
        admin_emails=" owner@example.com, team@example.com ,Owner@Example.com,",
    )
    notifier = EmailNotifier(settings)
    notifier._mailer = ResendMailer(settings, transport=transport)

    assert await notifier.send_lead_notification(
        subject="New enquiry", heading="New contact enquiry", fields={"Name": "Dina"}
    )

    assert sent(transport)["to"] == ["owner@example.com", "team@example.com"]


def test_blank_admin_emails_fall_back_to_the_notification_inbox() -> None:
    assert make_settings(admin_emails=" , ").lead_recipients == ["info@7magicwedding.com"]


@pytest.mark.asyncio
async def test_a_multi_line_lead_message_keeps_its_line_breaks_in_html() -> None:
    transport = RecordingTransport()
    settings = make_settings()
    notifier = EmailNotifier(settings)
    notifier._mailer = ResendMailer(settings, transport=transport)

    await notifier.send_lead_notification(
        subject="s",
        heading="h",
        fields={"Message": "LEAD: Paket Sangjit\nLokasi: <Jakarta>"},
    )

    # Escaped and broken, in that order: the angle brackets must not survive as
    # markup, and the break must not be escaped into visible text.
    assert "LEAD: Paket Sangjit<br>Lokasi: &lt;Jakarta&gt;" in sent(transport)["html"]


def test_an_unconfigured_notifier_reports_itself_as_such() -> None:
    assert EmailNotifier(make_settings(resend_api_key=None)).configured is False


@pytest.mark.asyncio
async def test_an_unconfigured_notifier_returns_false_without_sending() -> None:
    """A dev machine with no key must never post live mail, and must not raise."""
    notifier = EmailNotifier(make_settings(resend_api_key=None))

    result = await notifier.send_lead_notification(
        subject="s", heading="h", fields={"Name": "Dina"}
    )

    assert result is False
