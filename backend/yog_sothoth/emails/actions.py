"""Email actions."""
import logging
from email.message import Message
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional
from typing import Sequence

import aiosmtplib

from yog_sothoth.conf import settings

logger = logging.getLogger(__name__)


async def _send(message: Message, to: Sequence[str]) -> None:
    """Send an email message to a list of recipients asynchronously."""
    logger.info('Sending email to %s...', ', '.join(to))
    if settings.DEVELOPMENT_MODE:
        # Hardcode and bypass settings, this is done on purpose for dev mode.
        use_tls = start_tls = False
        port = 8025
        host = '127.0.0.1'
    else:
        port = settings.EMAIL_PORT
        host = settings.EMAIL_HOST
        use_tls = settings.EMAIL_USE_TLS
        start_tls = not use_tls
    logger.debug(
        'Email:\nmessage=%s\nhostname=%s\nport=%d\nusername=%s\npassword=%s\n'
        'recipients=%s\nuse_tls=%s\nstart_tls=%s\ntimeout=%d',
        message.get_payload(decode=True).decode(),
        host,
        port,
        settings.EMAIL_USERNAME,
        '[REDACTED]',
        str(to),
        use_tls,
        start_tls,
        settings.EMAIL_TIMEOUT,
    )
    try:
        response = await aiosmtplib.send(message,
                                         hostname=host,
                                         port=port,
                                         username=settings.EMAIL_USERNAME,
                                         password=settings.EMAIL_PASSWORD,
                                         recipients=to,
                                         use_tls=use_tls,
                                         start_tls=start_tls,
                                         timeout=settings.EMAIL_TIMEOUT)
    except aiosmtplib.errors.SMTPException:
        logger.exception('Email not sent because an error occurred')
    else:
        logger.debug('Email server response: %s', str(response))


def _get_message_body(body_plain: Optional[MIMEText],
                      body_html: Optional[MIMEText]) -> MIMEText:
    if not body_plain and not body_html:
        raise ValueError('Missing email body')

    if body_plain and body_html:
        message = MIMEMultipart('alternative')
        if body_plain:
            message.attach(body_plain)
        if body_html:
            message.attach(body_html)
    else:
        message = body_plain if body_plain else body_html

    return message


async def send(*,
               to: Sequence[str],
               subject: str,
               body_plain: Optional[MIMEText] = None,
               body_html: Optional[MIMEText] = None) -> None:
    """Send an email.

    Note that either `body_plain` or `body_html` must be specified, or both.

    :param to: Email recipients.
    :param subject: Email subject (will be appended to app's subject).
    :param body_plain: [optional] Plain text email body.
    :param body_html: [optional] HTML email body.
    """
    message = _get_message_body(body_plain, body_html)
    message['From'] = settings.EMAIL_SENDER_ADDRESS
    message['Subject'] = f'{settings.EMAIL_SUBJECT_PREFIX}{subject}'
    await _send(message, to)
