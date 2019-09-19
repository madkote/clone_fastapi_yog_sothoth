"""Registration endpoints."""

from typing import Dict
from typing import Tuple

from aioredis import Redis
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Header
from starlette import status

from yog_sothoth import crud
from yog_sothoth import objects
from yog_sothoth import schemas
from yog_sothoth.api.utils import get_cache

router = APIRouter()


# ToDo: https://www.starlette.io/authentication/


def _get_hidden_fields_for_manager() -> Tuple[str, ...]:
    return 'username', 'email', 'password', 'token'


async def get_object_or_404(cache: Redis, rid: str) -> objects.Registration:
    """Get a Registration object or raise 404 HTTPException."""
    registration = await crud.Registration(cache, rid=rid).read()
    if registration:
        return registration

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail='Registration not found')


async def _read(cache: Redis, authorization: str, rid: str) -> Dict[str, any]:
    """Read authorized registration object data."""
    registration = await get_object_or_404(cache, rid)

    if registration.verify_token(authorization):
        # It's a user
        for_manager = False
    elif registration.verify_manager_token(authorization):
        # It's a manager
        for_manager = True
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    hide = _get_hidden_fields_for_manager() if for_manager else None
    registration_data = registration.as_dict(hide=hide)
    return registration_data


@router.post('/', response_model=schemas.RegistrationInfo)
async def create(*,
                 cache: Redis = Depends(get_cache),
                 registration_new: schemas.RegistrationCreate):
    """Create a user registration.

    - **username**: unique user name
    - **email**: [optional] user email
    """
    registration = await crud.Registration(cache).create(registration_new)
    if not registration:
        raise HTTPException(status.HTTP_507_INSUFFICIENT_STORAGE,
                            detail='Create operation was not successful')
    # ToDo: Send notification to user too (maybe the email is not own? give chance
    #  to cancel it)
    # ToDo: wait for 5' before sending request to managers (to allow the user to
    #  cancel its reg)
    # ToDo: Send registration request email to managers
    registration_data = registration.as_dict()
    return registration_data


@router.get('/{rid}/', response_model=schemas.RegistrationInfoReduced)
async def read(*,
               cache: Redis = Depends(get_cache),
               authorization: str = Header(..., min_length=11, max_length=11),
               rid: str) -> Dict[str, any]:
    """Retrieve a user registration."""
    registration_data = await _read(cache, authorization, rid)
    return registration_data


@router.put('/{rid}/', response_model=schemas.RegistrationInfoReduced)
async def update(*,
                 cache: Redis = Depends(get_cache),
                 authorization: str = Header(..., min_length=11, max_length=11),
                 rid: str,
                 registration_update: schemas.RegistrationUpdate) -> Dict[str, any]:
    """Approve or reject a user registration."""
    registration = await get_object_or_404(cache, rid)

    if not registration.verify_manager_token(authorization):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    # It's a manager
    # ToDo: allow changes for only 5' after the first change
    registration = await crud.Registration(cache, rid=rid).update(registration_update)
    if not registration:
        raise HTTPException(status.HTTP_507_INSUFFICIENT_STORAGE,
                            detail='Update operation was not successful')
    # ToDo: Send registration request update email to user
    # ToDo: Send notification to managers
    # ToDo: if approved, send request to matrix
    registration_data = registration.as_dict(hide=_get_hidden_fields_for_manager())
    return registration_data


@router.delete('/{rid}/', response_model=schemas.RegistrationInfoReduced)
async def delete(*,
                 cache: Redis = Depends(get_cache),
                 authorization: str = Header(..., min_length=11, max_length=11),
                 rid: str) -> Dict[str, any]:
    """Delete a user registration."""
    registration_data = await _read(cache=cache, authorization=authorization, rid=rid)
    registration = await crud.Registration(cache, rid=rid).delete()
    if not registration:
        raise HTTPException(status.HTTP_507_INSUFFICIENT_STORAGE,
                            detail='Delete operation was not successful')
    # ToDo: Send notification to user
    # ToDo: Send notification to managers
    return registration_data
