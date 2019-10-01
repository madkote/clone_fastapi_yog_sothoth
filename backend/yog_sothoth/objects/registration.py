"""Registration object."""
import asyncio
import copy
import json
import logging
from dataclasses import dataclass
from dataclasses import field
from dataclasses import fields
from datetime import datetime
from secrets import token_urlsafe
from typing import Dict
from typing import Optional
from typing import Sequence
from typing import Set
from typing import Union

from aioredis import Redis

from yog_sothoth import schemas
from yog_sothoth.conf import settings
from yog_sothoth.utils.crypto import Hasher
from yog_sothoth.utils.json import JSONEncoder

logger = logging.getLogger(__name__)

TUnorderedSeqStr = Union[Sequence[str], Set[str]]


@dataclass
class Registration:
    """Registration dataclass."""

    cache: Optional[Redis] = field(default=None, hash=False, compare=False)
    rid: str = ''
    username: str = ''
    email: str = ''
    password: str = ''
    token: str = ''
    manager_token: str = ''
    status: str = schemas.RegistrationStatusEnum.pending
    matrix_status: str = schemas.MatrixRegStatusEnum.pending
    _creation: datetime = field(default_factory=datetime.now, init=False)
    _modification: datetime = field(default_factory=datetime.now, init=False)

    def __str__(self) -> str:
        """Human readable string representation."""
        return self.rid

    @staticmethod
    def _to_datetime(value: any) -> datetime:
        """Convert a value to a datetime object.

        :raises TypeError: Unsupported type for conversion.
        """
        if isinstance(value, datetime):
            return value
        elif isinstance(value, str):
            return datetime.fromisoformat(value)
        raise TypeError('Unsupported type for datetime conversion')

    @property
    def creation(self) -> datetime:
        """Get creation timestamp."""
        return self._creation

    @creation.setter
    def creation(self, value: Union[datetime, str]) -> None:
        """Set creation timestamp.

        :param value: A datetime object or an ISO formatted string.
        """
        self._creation = self._to_datetime(value)

    @property
    def modification(self) -> datetime:
        """Get modification timestamp."""
        return self._modification

    @modification.setter
    def modification(self, value: Union[datetime, str]) -> None:
        """Set modification timestamp.

        :param value: A datetime object or an ISO formatted string.
        """
        self._modification = self._to_datetime(value)

    def _asdict(self, *, exclude: Optional[TUnorderedSeqStr] = None) -> Dict[str, any]:
        """Convert `self` to a dictionary, optionally excluding some fields."""
        result = []
        for f in fields(self):
            name = f.name
            if name in exclude:
                continue  # Skip
            elif name[0] == '_' and hasattr(self, name[1:]):
                name = name[1:]  # Remove underscore for attributes that have public prop
            attr = copy.deepcopy(getattr(self, name))
            result.append((name, attr))
        return dict(result)

    async def as_dict(self,
                *,
                hashed: bool = False,
                hide: Optional[TUnorderedSeqStr] = None) -> Dict[str, any]:  # noqa: D202
        """Get object data as a dictionary.

        :param hashed: [optional] True to get secrets hashed.
        :param hide: [optional] Sequence of keys whose values are hidden from
                     the output (they are set as None).
        """
        data = self._asdict(exclude={'cache'})

        # ToDo: improve all of this
        if 'cache' in data:
            data.pop('cache')

        if hashed:
            hasher = Hasher()
            # Parallelize hashing
            loop = asyncio.get_running_loop()
            hashed_token_future = loop.run_in_executor(
                None,
                hasher.hash_if_not_hashed,
                self.token,
            )
            hashed_manager_token_future = loop.run_in_executor(
                None,
                hasher.hash_if_not_hashed,
                self.manager_token,
            )
            hashed_token, hashed_manager_token = await asyncio.gather(
                hashed_token_future,
                hashed_manager_token_future,
            )
            data['token'], data['manager_token'] = hashed_token, hashed_manager_token

        if hide:
            data.update({key: None for key in hide})

        return data

    def from_dict(self, data: Dict[str, any]) -> None:
        """Set the object properties from a dictionary.

        :param data: Dictionary to read.
        """
        if data:  # Prevent data being None
            for key, value in data.items():
                if hasattr(self, key):
                    setattr(self, key, value)

    async def as_json(self,
                      *,
                      hashed: bool = False,
                      hide: Optional[Sequence[str]] = None) -> str:
        """Get the object data as a JSON encoded string.

        :param hashed: [optional] True to get secrets hashed.
        :param hide: [optional] Sequence of keys whose values are hidden from
                     the output (they are set as None).
        """
        data = await self.as_dict(hashed=hashed, hide=hide)
        # Convert datetimes to string
        return json.dumps(data, cls=JSONEncoder)

    def from_json(self, json_data: str) -> None:
        """Set the object properties from a JSON string.

        :param json_data: JSON string to read.
        """
        data = json.loads(json_data)
        self.from_dict(data)

    def generate_rid(self) -> None:
        """Generate a random RID."""
        self.rid = token_urlsafe(4)

    def generate_token(self) -> None:
        """Generate a random token."""
        self.token = token_urlsafe(8)

    def generate_manager_token(self) -> None:
        """Generate a random manager token."""
        self.manager_token = token_urlsafe(8)

    def generate_password(self) -> None:
        """Generate a random password."""
        self.password = token_urlsafe(8)

    def verify_token(self, token: str) -> bool:
        """Verify user token."""
        return Hasher().verify(self.token, token)

    def verify_manager_token(self, token: str) -> bool:
        """Verify manager token."""
        return Hasher().verify(self.manager_token, token)

    def can_create_account(self) -> bool:
        """Validate if this registration is ready to create a Matrix account."""
        can_create = all((
            self.status == schemas.RegistrationStatusEnum.approved,
            self.matrix_status == schemas.MatrixRegStatusEnum.pending,
        ))
        return can_create

    async def save(self) -> bool:
        """Store itself in the cache.

        :return: True if storing is successful, False otherwise.
        """
        self.modification = datetime.now()
        json_data = await self.as_json(hashed=True)
        result = await self.cache.set(self.rid, json_data, expire=settings.CACHE_TTL)
        if not result:
            # There's no reason why saving would fail, so log it
            logger.warning('Saving registration data in the cache failed for data: %s',
                           json_data)
        return result

    async def retrieve(self) -> bool:
        """Retrieve itself from the cache.

        :return True for cache hit, False otherwise.
        """
        if not await self.cache.exists(self.rid):
            return False

        json_data = await self.cache.get(self.rid)
        self.from_json(json_data)
        return True

    async def delete(self) -> bool:
        """Delete itself from the cache.

        :return: True if deletion is successful, False otherwise.
        """
        if not await self.cache.exists(self.rid):
            return False

        result = bool(await self.cache.delete(self.rid))
        if not result:
            # There's no reason why deleting would fail, so log it
            logger.warning('Deleting registration data in the cache failed for key: %s',
                           self.rid)
        return result
