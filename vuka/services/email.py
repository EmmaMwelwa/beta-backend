import os
import smtplib
from email.message import EmailMessage


SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587

SMTP_USERNAME = os.getenv(
    "SMTP_USERNAME",
    "wanjirundjoroge@gmail.com",
)

SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

SMTP_FROM_EMAIL = os.getenv(
    "SMTP_FROM_EMAIL",
    "wanjirundjoroge@gmail.com",
)


def send_email(
    to_email: str,
    subject: str,
    body: str,
) -> None:
    if not SMTP_USERNAME:
        raise RuntimeError("SMTP_USERNAME is not configured.")

    if not SMTP_PASSWORD:
        raise RuntimeError("SMTP_PASSWORD is not configured.")

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = SMTP_FROM_EMAIL
    message["To"] = to_email
    message.set_content(body)

    try:
        with smtplib.SMTP(
            SMTP_HOST,
            SMTP_PORT,
            timeout=30,
        ) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()

            server.login(
                SMTP_USERNAME,
                SMTP_PASSWORD,
            )

            server.send_message(message)

    except smtplib.SMTPAuthenticationError as exc:
        raise RuntimeError(
            "Gmail authentication failed. "
            "Check the Gmail address and App Password."
        ) from exc

    except (smtplib.SMTPException, OSError) as exc:
        raise RuntimeError(
            f"Unable to send email through Gmail: {exc}"
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