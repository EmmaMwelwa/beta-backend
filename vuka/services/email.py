import base64
import os
from email.message import EmailMessage

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


GMAIL_SEND_SCOPE = "https://www.googleapis.com/auth/gmail.send"

GMAIL_SENDER_EMAIL = os.getenv(
    "GMAIL_SENDER_EMAIL",
    "joselyned321@gmail.com",
)

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REFRESH_TOKEN = os.getenv("GOOGLE_REFRESH_TOKEN")


def _get_gmail_service():
    if not GOOGLE_CLIENT_ID:
        raise RuntimeError(
            "GOOGLE_CLIENT_ID is not configured."
        )

    if not GOOGLE_CLIENT_SECRET:
        raise RuntimeError(
            "GOOGLE_CLIENT_SECRET is not configured."
        )

    if not GOOGLE_REFRESH_TOKEN:
        raise RuntimeError(
            "GOOGLE_REFRESH_TOKEN is not configured."
        )

    credentials = Credentials(
        token=None,
        refresh_token=GOOGLE_REFRESH_TOKEN,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        scopes=[GMAIL_SEND_SCOPE],
    )

    if not credentials.valid:
        credentials.refresh(Request())

    return build(
        "gmail",
        "v1",
        credentials=credentials,
        cache_discovery=False,
    )


def send_email(
    to_email: str,
    subject: str,
    body: str,
) -> None:
    message = EmailMessage()

    message["From"] = GMAIL_SENDER_EMAIL
    message["To"] = to_email
    message["Subject"] = subject

    message.set_content(body)

    encoded_message = base64.urlsafe_b64encode(
        message.as_bytes()
    ).decode("utf-8")

    try:
        service = _get_gmail_service()

        service.users().messages().send(
            userId="me",
            body={
                "raw": encoded_message,
            },
        ).execute()

    except HttpError as exc:
        raise RuntimeError(
            f"Gmail API email delivery failed: {exc}"
        ) from exc

    except Exception as exc:
        raise RuntimeError(
            f"Unable to send email through Gmail API: {exc}"
        ) from exc


def send_password_reset_email(
    to_email: str,
    reset_token: str,
) -> None:
    frontend_url = os.getenv(
        "FRONTEND_URL",
        "http://localhost:3000",
    )

    reset_link = (
        f"{frontend_url}/reset-password"
        f"?token={reset_token}"
    )

    subject = "Reset your password"

    body = (
        "We received a request to reset your password.\n\n"
        "Click the link below to choose a new password:\n"
        f"{reset_link}\n\n"
        "This link expires in 30 minutes. "
        "If you didn't request this, "
        "you can safely ignore this email."
    )

    send_email(
        to_email,
        subject,
        body,
    )