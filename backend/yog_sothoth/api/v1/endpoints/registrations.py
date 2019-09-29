"""Registration endpoints."""
from typing import Dict
from typing import Tuple

from aioredis import Redis
from fastapi import APIRouter
from fastapi import BackgroundTasks
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Path
from starlette import status

from yog_sothoth import crud
from yog_sothoth import schemas
from yog_sothoth import tasks
from yog_sothoth.api import auth
from yog_sothoth.api.utils import get_cache

router = APIRouter()


def _get_hidden_fields_for_manager() -> Tuple[str, ...]:
    return 'username', 'email', 'password', 'token', 'manager_token'


@router.post('/', response_model=schemas.RegistrationInfo)
async def create_registration_request(
        *,
        cache: Redis = Depends(get_cache),
        registration_new: schemas.RegistrationCreate,
        background_tasks: BackgroundTasks,
) -> Dict[str, any]:
    """Create a registration request.

    - **email**: [optional] address to receive notifications.
    """
    registration_crud = crud.Registration(cache)

    if not await registration_crud.create(registration_new):
        raise HTTPException(status.HTTP_507_INSUFFICIENT_STORAGE,
                            detail='Create operation failed for an unknown reason')

    if registration_crud.registration.email:
        background_tasks.add_task(tasks.task_notify_user_registration_received,
                                  registration_crud.registration)
    # ToDo: wait for 5' before sending request to managers (to allow the user to
    #  cancel its reg)
    background_tasks.add_task(tasks.task_notify_managers_registration_received,
                              registration_crud.registration)

    return registration_crud.registration.as_dict()


@router.get('/{rid}/', response_model=schemas.RegistrationInfoReduced)
async def read_registration_request(
        *,
        cache: Redis = Depends(get_cache),
        api_user: auth.APIUser = Depends(auth.authenticate_request),
        rid: str = Path(..., min_length=6, max_length=6, title='Registration ID'),
) -> Dict[str, any]:
    """Retrieve a registration request (requires user or manager authentication).

    Authentication:
    - **username**: registration id.
    - **password**: token.
    """
    # Verify resource permission
    if api_user.rid != rid:
        raise auth.AccessDeniedException()

    # Verify access permission
    # Both users and managers can access this, the response changes for each

    registration_crud = crud.Registration(cache, rid=rid)
    await registration_crud.read()  # Exists because the credentials are valid

    hide = _get_hidden_fields_for_manager() if api_user.is_manager else None
    return registration_crud.registration.as_dict(hide=hide)


@router.put('/{rid}/', response_model=schemas.RegistrationInfoReduced)
async def approve_or_reject_registration_request(
        *,
        cache: Redis = Depends(get_cache),
        api_user: auth.APIUser = Depends(auth.authenticate_request),
        rid: str = Path(..., min_length=6, max_length=6, title='Registration ID'),
        registration_update: schemas.RegistrationUpdateByManager,
        background_tasks: BackgroundTasks,
) -> Dict[str, any]:
    """Approve or reject a registration request (requires manager authentication).

    Authentication:
    - **username**: registration id.
    - **password**: token.
    """
    # Verify resource permission
    if api_user.rid != rid:
        raise auth.AccessDeniedException()

    # Verify access permission
    if not api_user.is_manager:
        raise auth.AccessDeniedException()

    # ToDo: allow changes for only 5' after the first change
    # Allow status change only once
    registration_crud = crud.Registration(cache, rid=rid)
    await registration_crud.read()  # Exists because the credentials are valid

    if registration_crud.registration.status != schemas.RegistrationStatusEnum.pending:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail='This registration status has already been set')

    if not await registration_crud.update(registration_update):
        raise HTTPException(status.HTTP_507_INSUFFICIENT_STORAGE,
                            detail='Update operation failed for an unknown reason')

    if registration_crud.registration.email:
        background_tasks.add_task(tasks.task_notify_user_status_changed,
                                  registration_crud.registration)
    background_tasks.add_task(tasks.task_notify_managers_status_changed,
                              registration_crud.registration)

    hide = _get_hidden_fields_for_manager()
    return registration_crud.registration.as_dict(hide=hide)


@router.patch('/{rid}/', response_model=schemas.RegistrationInfoReduced)
async def create_account_once_approved(
        *,
        cache: Redis = Depends(get_cache),
        api_user: auth.APIUser = Depends(auth.authenticate_request),
        rid: str = Path(..., min_length=6, max_length=6, title='Registration ID'),
        registration_update: schemas.RegistrationUpdateByUser,
        background_tasks: BackgroundTasks,
) -> Dict[str, any]:
    """Create a Matrix account (requires user authentication).

    The account can only be created once the registration request is approved.

    Authentication:
    - **username**: registration id.
    - **password**: token.
    """
    # Verify resource permission
    if api_user.rid != rid:
        raise auth.AccessDeniedException()

    # Verify access permission
    if api_user.is_manager:
        raise auth.AccessDeniedException()

    registration_crud = crud.Registration(cache, rid=rid)
    await registration_crud.read()  # Exists because the credentials are valid

    if not registration_crud.registration.can_create_account():
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail='The registration request is not yet approved or '
                                   'already in process')

    if not registration_update.email:
        registration_update.email = registration_crud.registration.email
    update = schemas.RegistrationUpdateMatrixStatus(**registration_update.dict())
    if not await registration_crud.update(update):
        raise HTTPException(status.HTTP_507_INSUFFICIENT_STORAGE,
                            detail='Update operation failed for an unknown reason')

    # Don't get password from user, create instead
    registration_crud.registration.generate_password()
    registration_crud.registration.username = registration_update.username

    background_tasks.add_task(tasks.task_create_matrix_account,
                              registration_crud.registration)

    return registration_crud.registration.as_dict()


@router.delete('/{rid}/', response_model=schemas.RegistrationInfoReduced)
async def delete_registration_request(
        *,
        cache: Redis = Depends(get_cache),
        api_user: auth.APIUser = Depends(auth.authenticate_request),
        rid: str = Path(..., min_length=6, max_length=6, title='Registration ID'),
) -> Dict[str, any]:
    """Delete a registration request (requires user authentication).

    Note that registration requests are automatically deleted, no matter what,
    after certain given time.

    Authentication:
    - **username**: registration id.
    - **password**: token.
    """
    # Verify resource permission
    if api_user.rid != rid:
        raise auth.AccessDeniedException()

    # Verify access permission
    if api_user.is_manager:
        raise auth.AccessDeniedException()

    registration_crud = crud.Registration(cache, rid=rid)

    if not await registration_crud.delete():
        raise HTTPException(status.HTTP_507_INSUFFICIENT_STORAGE,
                            detail='Delete operation failed for an unknown reason')

    return registration_crud.registration.as_dict()
