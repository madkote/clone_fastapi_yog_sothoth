"""Registration CRUD class."""
from typing import Optional
from typing import Union

from aioredis import Redis

from yog_sothoth import objects
from yog_sothoth import schemas

TCreate = schemas.RegistrationCreate
TUpdate = Union[schemas.RegistrationUpdateByManager,
                schemas.RegistrationUpdateMatrixStatus]


class Registration:
    """Cache manager class for a registration."""

    __slots__ = ('cache', 'rid', '_registration')

    def __init__(self, cache: Redis, *, rid: Optional[str] = None,
                 registration: Optional[objects.Registration] = None):
        """Manage Registration objects in the cache.

        :param cache: Cache to use.
        :param rid: [optional] Unique registration identifier.
        :param registration: [optional] An already fetched Registration object.
        """
        self.cache: Redis = cache
        self.rid: str = rid if rid else ''
        self._registration: Optional[objects.Registration] = registration

    @property
    def registration(self) -> Optional[objects.Registration]:
        """Get a fetched Registration object if any."""
        return self._registration

    async def _ensure_registration(self) -> None:
        if not self._registration:
            await self.read()

    async def create(self, data: TCreate) -> bool:
        """Create a new registration in the cache.

        :param data: Registration schema model.
        :return: True if a registration is created, False otherwise.
        """
        self._registration = objects.Registration(**data.dict(), cache=self.cache)
        self._registration.generate_rid()
        self._registration.generate_token()
        self._registration.generate_manager_token()
        if not await self._registration.save():
            self._registration = None
        return bool(self._registration)

    async def read(self) -> bool:
        """Retrieve registration information from the cache.

        This method always retrieves from the cache, overwriting any previously
        retrieved object if any.

        :return: True if a registration is retrieved, False otherwise.
        """
        self._registration = objects.Registration(cache=self.cache, rid=self.rid)
        if not await self._registration.retrieve():
            self._registration = None
        return bool(self._registration)

    async def update(self, data: TUpdate) -> bool:
        """Update an existing registration.

        Retrieves the object first if it wasn't retrieved yet.

        :param data: Registration update schema model.
        :return: True if the registration is updated, False otherwise.
        """
        await self._ensure_registration()
        if self._registration:
            self._registration.from_dict(data.dict())
            if not await self._registration.save():
                self._registration = None
        return bool(self._registration)

    async def delete(self) -> bool:
        """Delete an existing registration object.

        Retrieves the object first if it wasn't retrieved yet.

        :return: True if the registration is deleted, False otherwise.
        """
        await self._ensure_registration()
        if self._registration:
            if await self._registration.delete():
                self._registration.status = schemas.RegistrationStatusEnum.deleted
            else:
                self._registration = None
        return bool(self._registration)
