"""Notifications tasks."""
from email.mime.text import MIMEText
from typing import List
from typing import Optional
from typing import Sequence

from yog_sothoth import emails
from yog_sothoth import messages
from yog_sothoth import schemas
from yog_sothoth.conf import settings
from yog_sothoth.connectors import matrix
from yog_sothoth.objects import Registration


# ToDo: please, please, refactor this


async def _notify_from_parts(subject: str,
                             to: Sequence[str],
                             *,
                             message_parts_pt: Optional[Sequence[str]] = None,
                             message_parts_html: Optional[Sequence[str]] = None) -> None:
    """Send a notification from message parts."""
    # noinspection PyArgumentEqualDefault
    body_plain = (
        MIMEText('\n'.join(message_parts_pt), 'plain', 'utf-8')
        if message_parts_pt
        else None
    )
    body_html = (
        MIMEText('\n'.join(message_parts_html), 'html', 'utf-8')
        if message_parts_html
        else None
    )
    await emails.send(to=to, subject=subject, body_plain=body_plain,
                      body_html=body_html)


async def _finish_message(subject: str,
                          to: Sequence[str],
                          *,
                          message_parts_pt: Optional[Sequence[str]] = None,
                          message_parts_html: Optional[Sequence[str]] = None) -> None:
    if settings.FRONTEND_URL:
        message_parts_pt.extend(
            messages.generic.frontend_propaganda(settings.FRONTEND_URL),
        )
    message_parts_pt.extend(
        messages.generic.status_changes_repetition(),
    )
    if settings.CONTACT_ADDRESS:
        message_parts_pt.extend(
            messages.generic.contact_address(settings.CONTACT_ADDRESS),
        )
    message_parts_pt.extend(
        messages.generic.signature(),
    )
    await _notify_from_parts(subject, to, message_parts_pt=message_parts_pt,
                             message_parts_html=message_parts_html)


async def _finish_user_message(registration: Registration,
                               message_parts_pt: List[str],
                               subject: str) -> None:
    await _finish_message(subject, [registration.email],
                          message_parts_pt=message_parts_pt)


async def _finish_managers_message(registration: Registration,
                                   message_parts_pt: List[str],
                                   subject: str) -> None:
    await _finish_message(subject, settings.MANAGERS_ADDRESSES,
                          message_parts_pt=message_parts_pt)


async def task_notify_user_registration_received(registration: Registration) -> None:
    """Task to notify a user that its registration has been received."""
    subject = 'Registration received'

    user_name = registration.email.split('@')[0]
    message_parts_pt = messages.user.salutation(user_name)
    message_parts_pt.extend(
        messages.generic.action_new_registration(settings.MATRIX_URL),
    )
    message_parts_pt.extend(
        messages.user.registration_information(registration.rid,
                                               registration.token),
    )
    message_parts_pt.extend(
        messages.user.curl_registration_status(registration.rid, registration.token),
    )
    message_parts_pt.extend(
        messages.user.curl_delete_registration(registration.rid, registration.token),
    )

    await _finish_user_message(registration, message_parts_pt, subject)


async def task_notify_user_status_changed(registration: Registration) -> None:
    """Task to notify a user that the registration status changed."""
    subject = 'Registration status changed'

    user_name = registration.email.split('@')[0]
    message_parts_pt = messages.user.salutation(user_name)
    message_parts_pt.extend(messages.generic.status_changed(registration.status,
                                                            registration.rid))
    if registration.status == schemas.RegistrationStatusEnum.approved:
        message_parts_pt.extend(
            messages.user.status_approved(registration.rid, '<your token>'),
        )

    await _finish_user_message(registration, message_parts_pt, subject)


async def task_notify_user_matrix_status_changed(
        registration: Registration, *, account: Optional[matrix.MatrixAccount] = None,
) -> None:
    """Task to notify a user that the matrix registration status changed."""
    subject = 'Matrix registration status changed'

    message_parts_pt = messages.user.salutation(registration.username)
    message_parts_pt.extend(
        messages.generic.status_changed(registration.matrix_status, registration.rid,
                                        matrix=True),
    )
    if account:
        message_parts_pt.extend(
            messages.user.matrix_account_created(account.user_id, account.home_server),
        )
    await _finish_user_message(registration, message_parts_pt, subject)


async def task_notify_managers_registration_received(registration: Registration) -> None:
    """Task to notify the managers that a registration has been received."""
    subject = 'Registration received'

    message_parts_pt = messages.manager.salutation()
    message_parts_pt.extend(
        messages.generic.action_new_registration(settings.MATRIX_URL),
    )
    message_parts_pt.extend(
        messages.generic.registration_information(registration.rid,
                                                  registration.manager_token),
    )
    message_parts_pt.extend(
        messages.manager.curl_registration_status(registration.rid,
                                                  registration.manager_token),
    )
    message_parts_pt.extend(
        messages.manager.curl_change_registration_status(registration.rid,
                                                         registration.manager_token),
    )

    await _finish_managers_message(registration, message_parts_pt, subject)


async def task_notify_managers_status_changed(registration: Registration) -> None:
    """Task to notify the managers that the registration status changed."""
    subject = 'Registration status changed'

    message_parts_pt = messages.manager.salutation()
    message_parts_pt.extend(
        messages.generic.status_changed(registration.status, registration.rid),
    )

    await _finish_managers_message(registration, message_parts_pt, subject)


async def task_notify_managers_matrix_status_changed(registration: Registration) -> None:
    """Task to notify the managers that the matrix registration status changed."""
    subject = 'Matrix registration status changed'

    message_parts_pt = messages.manager.salutation()
    message_parts_pt.extend(
        messages.generic.status_changed(registration.matrix_status, registration.rid,
                                        matrix=True),
    )

    await _finish_managers_message(registration, message_parts_pt, subject)
