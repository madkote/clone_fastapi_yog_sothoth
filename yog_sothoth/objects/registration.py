"""Registration object."""
import copy
import json
import logging
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from multiprocessing import cpu_count
from secrets import token_urlsafe
from typing import Dict
from typing import Optional
from typing import Sequence

import argon2
from aioredis import Redis

from yog_sothoth import schemas
from yog_sothoth import settings
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
    registration_status: str = schemas.MatrixRegStatusEnum.pending
    creation: datetime = field(default_factory=datetime.now)
    modification: datetime = field(default_factory=datetime.now)

    def __str__(self) -> str:
        """Human readable string representation."""
        return self.rid

    def _verify_token(self, hash_: str, token: str) -> bool:
        """Verify a token against its hash."""
        hasher = self._hasher
        try:
            return hasher.verify(hash_, token)
        except argon2.exceptions.VerifyMismatchError:
            return False
        except (argon2.exceptions.VerificationError, argon2.exceptions.InvalidHash) as e:
            logger.error(
                'Unexpected error while verifying a token (hash=%s, token=%s): %s',
                hash_,
                token,
                repr(e),
            )
        return False

    @property
    def _hasher(self) -> argon2.PasswordHasher:
        """Get secrets hasher."""
        return argon2.PasswordHasher(
            parallelism=cpu_count() * 2,
            memory_cost=argon2.DEFAULT_MEMORY_COST * 2,
            time_cost=argon2.DEFAULT_TIME_COST * 2,
        )
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

    def as_dict(self,
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
            hasher = self._hasher
            data['token'] = (
                self.token
                if is_hashed(self.token)
                else hasher.hash(self.token)
            )
            data['manager_token'] = (
                self.manager_token
                if is_hashed(self.manager_token)
                else hasher.hash(self.manager_token)
            )

        if hide:
            data.update({key: None for key in hide})

        # ToDo: encrypt password with token
        return data

    def from_dict(self, data: Dict[str, any]) -> None:
        """Set the object properties from a dictionary.

        :param data: Dictionary to read.
        """
        if data:  # Prevent data being None
            for key, value in data.items():
                if hasattr(self, key):
                    setattr(self, key, value)

    def as_json(self,
                *,
                hashed: bool = False,
                hide: Optional[Sequence[str]] = None) -> str:
        """Get the object data as a JSON encoded string.

        :param hashed: [optional] True to get secrets hashed.
        :param hide: [optional] Sequence of keys whose values are hidden from
                     the output (they are set as None).
        """
        data = self.as_dict(hashed=hashed, hide=hide)
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
        return self._verify_token(self.token, token)

    def verify_manager_token(self, token: str) -> bool:
        """Verify manager token."""
        return self._verify_token(self.manager_token, token)

    async def save(self) -> bool:
        """Store itself in the cache.

        :return: True if storing is successful, False otherwise.
        """
        self.modification = datetime.now()
        json_data = self.as_json(hashed=True)
        return await self.cache.set(self.rid, json_data, expire=settings.CACHE_TTL)

    async def retrieve(self) -> bool:
        """Retrieve itself from the cache.

        :return True for cache hit, False otherwise.
        """
        if not self.cache.exists(self.rid):
            return False

        json_data = await self.cache.get(self.rid)
        self.from_json(json_data)
        return True

    async def delete(self) -> bool:
        """Delete itself from the cache.

        :return: True if deletion is successful, False otherwise.
        """
        if self.cache.exists(self.rid):
            return bool(await self.cache.delete(self.rid))
        return False
