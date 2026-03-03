from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import aiosmtplib

from ..configuration import settings
from .logger import retrieve_logger

_LOGGER = retrieve_logger(__name__)


async def send_email(
    recipient: str,
    subject: str,
    body_html: str,
) -> None:
    message = MIMEMultipart("alternative")
    message["From"] = settings.smtp.sender
    message["To"] = recipient
    message["Subject"] = subject
    message.attach(MIMEText(body_html, "html"))

    try:
        await aiosmtplib.send(
            message,
            hostname=settings.smtp.host,
            port=settings.smtp.port,
            username=settings.smtp.username,
            password=settings.smtp.password,
        )
        _LOGGER.info(f"Email sent to {recipient}: {subject}")
    except Exception as exception:
        _LOGGER.error(f"Failed to send email to {recipient}: {exception}")
        raise
