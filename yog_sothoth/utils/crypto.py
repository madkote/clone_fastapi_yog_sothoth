"""Some cryptographic utilities."""
import logging
from abc import ABC
from abc import abstractmethod
from multiprocessing import cpu_count
from typing import Tuple
from typing import Union

import argon2

logger = logging.getLogger(__name__)

TParam = Union[bytes, str, bytearray]


class OTPCypher:
    """One-time pad cypher (use with extreme care!).

    There are several restrictions for this to work: both parameters must have
    the same byte length (meaning: be careful with non-ascii characters), and
    the OTP parameter must truly be unique (if it is repeated, the encryption
    can be broken). Additionally, no parameter must be controlled by the user
    because this algorithm is malleable.
    If that holds, then this encryption is information-theoretically secure.
    """

    @staticmethod
    def _check_param_before_conversion(param: TParam) -> bool:
        if not isinstance(param, (bytes, str, bytearray)):
            raise TypeError('Both parameters must be an instance of bytes, str or '
                            'bytearray')
        return True

    @classmethod
    def _check_params_before_conversion(cls, p1: TParam, p2: TParam) -> bool:
        return all((cls._check_param_before_conversion(p1),
                    cls._check_param_before_conversion(p2)))

    @staticmethod
    def _convert_param_to_process(param: TParam) -> bytearray:
        if isinstance(param, str):
            return bytearray(param, 'utf-8')
        return bytearray(param)

    @staticmethod
    def _check_params_before_process(p1: bytearray, p2: bytearray) -> bool:
        if not isinstance(p1, bytearray) or not isinstance(p2, bytearray):
            raise TypeError('Both parameters must be an instance of bytearray')
        if len(p1) != len(p2):
            raise ValueError('Both parameters must be of the same length')
        return True

    @classmethod
    def _convert_params_to_process(cls,
                                   p1: TParam,
                                   p2: TParam) -> Tuple[bytearray, bytearray]:
        cls._check_params_before_conversion(p1, p2)
        p1_c, p2_c = (cls._convert_param_to_process(p1),
                      cls._convert_param_to_process(p2))
        cls._check_params_before_process(p1_c, p2_c)
        return p1_c, p2_c

    @staticmethod
    def _convert_to_output(value: bytearray) -> str:
        return value.decode('utf-8')

    @classmethod
    def encrypt_decrypt(cls, key: TParam, pt_ct: TParam) -> str:
        """Encrypt or decrypt given parameters.

        :param key: Key parameter that will be used to encrypt or decrypt.
        :param pt_ct: Either plain text to encrypt or cypher text to decrypt.
        :return: The result of XORing each byte of both parameters, as UTF-8
                 string.
        """
        # ToDo: maybe use a short header to know whether it's encrypted or not
        key_p, pt_ct_p = cls._convert_params_to_process(key, pt_ct)
        processed = bytearray(p1 ^ p2 for p1, p2 in zip(key_p, pt_ct_p))
        return cls._convert_to_output(processed)


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
            parallelism=cpu_count() * 2,
            memory_cost=argon2.DEFAULT_MEMORY_COST * 2,
            time_cost=argon2.DEFAULT_TIME_COST * 2,
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
    def is_hashed(value: str) -> bool:
        """Check if a value is hashed or not."""
        try:
            argon2.extract_parameters(value)
            hashed = True
        except argon2.exceptions.InvalidHash:
            hashed = False
        return hashed
