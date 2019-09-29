"""Matrix-related tasks."""
import logging
from typing import Optional

from yog_sothoth import crud
from yog_sothoth import objects
from yog_sothoth import schemas
from yog_sothoth.conf import settings
from yog_sothoth.connectors import matrix
from .notifications import task_notify_managers_matrix_status_changed
from .notifications import task_notify_user_matrix_status_changed

logger = logging.getLogger(__name__)


async def _create_matrix_account(
        registration: objects.Registration,
) -> Optional[matrix.MatrixAccount]:
    if settings.DEVELOPMENT_MODE:
        logger.info('Faking Matrix API...')
        server_url = 'http://127.0.0.1:8000/v1/matrix'
        registration_shared_secret = 'fakesecret'  # noqa: S105  # nosec
    else:
        server_url = settings.MATRIX_URL
        registration_shared_secret = settings.MATRIX_REGISTRATION_SHARED_SECRET
    connector = matrix.Matrix(
        server_url=server_url,
        registration=registration,
        timeout=settings.REQUESTS_TIMEOUT,
        registration_shared_secret=registration_shared_secret,
    )
    try:
        account = await connector.create_account()
    except matrix.MatrixError:
        logger.exception('Error while trying to create a Matrix account for %s',
                         registration.rid)
        # ToDo: maybe retry a couple of times?
        account = None
    else:
        logger.info('Matrix account created successfully for %s', registration.rid)
    return account


async def task_create_matrix_account(registration: objects.Registration) -> None:
    """Create a matrix account."""
    account = await _create_matrix_account(registration)

    # Change and save status
    # ToDo: maybe this shouldn't be here?
    if account:
        registration.matrix_status = schemas.MatrixRegStatusEnum.success
    else:
        registration.matrix_status = schemas.MatrixRegStatusEnum.failed
    update = schemas.RegistrationUpdateMatrixStatus(
        matrix_status=registration.matrix_status,
        email=registration.email,
    )
    await crud.Registration(registration.cache, rid=registration.rid).update(update)

    # Notify
    if registration.email:
        await task_notify_user_matrix_status_changed(registration, account=account)
    await task_notify_managers_matrix_status_changed(registration)
