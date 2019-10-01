"""Some cryptographic utilities."""
import logging
from abc import ABC
from abc import abstractmethod
from typing import Union

import argon2

from yog_sothoth.conf import settings

logger = logging.getLogger(__name__)


class HasherBaseInterface(ABC):
    """Abstract base class for a hasher."""

    __slots__ = ('_hasher',)

    @abstractmethod  # noqa: A003
    def hash(self, value: Union[bytes, str]) -> str:
        """Get the value hashed."""

    @abstractmethod
    def verify(self, hashed: str, value: Union[bytes, str]) -> bool:
        """Verify if a value matches its hash."""

    @staticmethod
    @abstractmethod
    def is_hashed(value: str) -> bool:
        """Check if a value is hashed or not."""


class Hasher(HasherBaseInterface):
    """A class to hash and verify hashed values."""

    def __init__(self):
        """Hash and verify values."""
        self._hasher = argon2.PasswordHasher(
            parallelism=settings.ARGON2_PARALLELISM,
            memory_cost=settings.ARGON2_MEMORY_COST,
            time_cost=settings.ARGON2_TIME_COST,
        )

    def hash(self, value: Union[bytes, str]) -> str:  # noqa: A003
        """Get the value hashed."""
        return self._hasher.hash(value)

    def verify(self, hashed: str, value: Union[bytes, str]) -> bool:
        """Verify if a value matches its hash."""
        try:
            return self._hasher.verify(hashed, value)
        except argon2.exceptions.VerifyMismatchError:
            return False
        except (argon2.exceptions.VerificationError, argon2.exceptions.InvalidHash) as e:
            logger.warning(
                'Unexpected error while verifying a value (hash=%s, token=%s): %s',
                hashed,
                value,
                repr(e),
            )
        return False

    @staticmethod
    def is_hashed(value: Union[bytes, str]) -> bool:
        """Check if a value is hashed or not."""
        if not isinstance(value, str):
            return False

        try:
            argon2.extract_parameters(value)
            hashed = True
        except argon2.exceptions.InvalidHash:
            hashed = False
        return hashed

    def hash_if_not_hashed(self, value: Union[bytes, str]) -> str:
        """Check if a value is hashed and if not, hash it.

        :return: Hashed value.
        """
        if self.is_hashed(value):
            return value
        return self.hash(value)
