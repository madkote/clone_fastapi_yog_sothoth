"""Registration CRUD class."""
from typing import Optional

from aioredis import Redis

from yog_sothoth import objects
from yog_sothoth import schemas


class Registration:
    """Cache manager class for a registration."""

    __slots__ = ('cache', 'rid')

    def __init__(self, cache: Redis, *, rid: Optional[str] = None):
        """Manage models in the cache.

        :param cache: Cache to use.
        :param rid: [optional] Unique registration identifier.
        """
        self.cache: Redis = cache
        self.rid: str = rid if rid else ''

    async def create(self,
                     data: schemas.RegistrationCreate) -> Optional[objects.Registration]:
        """Create a new registration in the cache.

        :param data: Registration schema model.
        :return: Created registration object if any.
        """
        registration = objects.Registration(**data.dict())
        registration.generate_rid()
        registration.generate_token()
        registration.generate_manager_token()
        registration.cache = self.cache
        if await registration.save():
            return registration

    async def read(self) -> Optional[objects.Registration]:
        """Retrieve registration information from the cache, if any.

        :return: Registration object from the cache.
        """
        registration = objects.Registration(cache=self.cache, rid=self.rid)
        if await registration.retrieve():
            return registration

    async def update(self,
                     data: schemas.RegistrationUpdate) -> Optional[objects.Registration]:
        """Update an existing registration.

        :param data: Registration update schema model.
        :return: Updated registration object.
        """
        registration = objects.Registration(cache=self.cache, rid=self.rid)
        if await registration.retrieve():
            registration.status = data.status
            if await registration.save():
                return registration

    async def delete(self) -> Optional[objects.Registration]:
        """Delete an existing registration object.

        :return: Deleted registration object.
        """
        registration = objects.Registration(cache=self.cache, rid=self.rid)
        if await registration.retrieve():
            if await registration.delete():
                registration.status = schemas.RegistrationStatusEnum.rejected
                return registration
