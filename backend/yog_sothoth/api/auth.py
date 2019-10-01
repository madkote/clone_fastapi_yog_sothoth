"""API authentication elements."""
import asyncio
from typing import NamedTuple

from aioredis import Redis
from fastapi import Depends
from fastapi import HTTPException
from fastapi.security import HTTPBasic
from fastapi.security import HTTPBasicCredentials
from pydantic import ValidationError
from starlette import status

from yog_sothoth import crud
from yog_sothoth import schemas
from yog_sothoth.api.utils import get_cache

security = HTTPBasic()


class APIUser(NamedTuple):
    """Application authenticated user."""

    is_manager: bool
    rid: str


class AccessDeniedException(HTTPException):
    """Access denied exception.

    To be raised when the user is not authorized for the requested action.
    """

    def __init__(self) -> None:
        """Access denied exception (user not authorized for requested action)."""
        super().__init__(status.HTTP_403_FORBIDDEN, 'Incorrect RID or Token')


class InvalidUserCredentialsException(HTTPException):
    """Invalid user credentials exception.

    To be raised when the user fails authentication.
    """

    def __init__(self) -> None:
        """Invalid user credentials exception (user failed authentication)."""
        super().__init__(status.HTTP_401_UNAUTHORIZED,
                         'Incorrect RID or Token',
                         {'WWW-Authenticate': 'Basic'})


async def authenticate_request(
        *,
        cache: Redis = Depends(get_cache),
        credentials: HTTPBasicCredentials = Depends(security),
) -> APIUser:
    """Authenticate a request against credentials stored in the cache.

    :param cache: A Redis cache.
    :param credentials: Credentials received.
    :return: An APIUser object.
    :raises InvalidUserCredentialsException: Authentication failed.
    """
    # I can't pass the schema model directly to the security class so I'm checking
    # schema here.
    try:
        creds = schemas.UserAuthBasic(rid=credentials.username,
                                      token=credentials.password)
    except ValidationError:
        raise InvalidUserCredentialsException()

    registration_crud = crud.Registration(cache, rid=creds.rid)
    if not await registration_crud.read():
        raise HTTPException(status.HTTP_404_NOT_FOUND,
                            detail='Registration request not found')

    # Run verifications in parallel
    loop = asyncio.get_running_loop()
    is_user_future = loop.run_in_executor(
        None,
        registration_crud.registration.verify_token,
        creds.token,
    )
    is_manager_future = loop.run_in_executor(
        None,
        registration_crud.registration.verify_manager_token,
        creds.token,
    )
    is_user, is_manager = await asyncio.gather(is_user_future, is_manager_future)

    if any((is_user, is_manager)):
        return APIUser(is_manager=is_manager, rid=creds.rid)

    raise InvalidUserCredentialsException()
