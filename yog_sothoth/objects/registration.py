"""Registration object."""
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
from yog_sothoth import settings
from yog_sothoth.utils.crypto import Hasher
from yog_sothoth.utils.crypto import OTPCypher
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
            hasher = Hasher()
            data['token'] = (
                self.token
                if hasher.is_hashed(self.token)
                else hasher.hash(self.token)
            )
            data['manager_token'] = (
                self.manager_token
                if hasher.is_hashed(self.manager_token)
                else hasher.hash(self.manager_token)
            )
            # Encrypt password if it's not encrypted
            # I can't actually know if the password is encrypted or not, but
            # I assume it is when the token is hashed.
            data['password'] = (
                self.password
                if hasher.is_hashed(self.token)
                else OTPCypher.encrypt_decrypt(self.token, self.password)
            )
            # ToDo: encrypt username and email

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

    def decrypt_password(self) -> None:
        """Decrypts an encrypted password using an unhashed token.

        Only call if you know that the password is encrypted and that the token
        is not hashed.
        """
        self.password = OTPCypher.encrypt_decrypt(self.token, self.password)

    def verify_token(self, token: str) -> bool:
        """Verify user token."""
        return Hasher().verify(self.token, token)

    def verify_manager_token(self, token: str) -> bool:
        """Verify manager token."""
        return Hasher().verify(self.manager_token, token)

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
