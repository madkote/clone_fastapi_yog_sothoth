"""Registration request schemas."""
import re
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel
from pydantic import EmailStr
from pydantic import Schema
from pydantic import validator


class RegistrationStatusEnum(str, Enum):
    """User status options."""

    pending = 'pending'
    approved = 'approved'
    rejected = 'rejected'


class MatrixRegStatusEnum(str, Enum):
    """User registration status options."""

    pending = 'pending'
    success = 'success'
    failed = 'failed'


class RegistrationCreate(BaseModel):
    """Schema model class to create a new registration."""

    username: str = Schema(..., max_length=140)
    email: EmailStr = Schema('', max_length=140)

    # noinspection PyMethodParameters
    @validator('username')
    def username_chars(cls, value) -> str:  # noqa: N805
        """Validate username characters."""
        if re.match(r'^([\w.-]+)$', value):
            return value
        raise ValueError('username can only be alphanumeric with symbols: _.-')


class RegistrationInfoReduced(BaseModel):
    """Schema model class for reduced registration information."""

    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    rid: str = Schema(..., max_length=6)  # 4B
    status: RegistrationStatusEnum = RegistrationStatusEnum.pending
    registration_status: MatrixRegStatusEnum = MatrixRegStatusEnum.pending
    creation: datetime = Schema(...)  # Unix time
    modification: datetime = Schema(...)  # Unix time


class RegistrationInfo(RegistrationInfoReduced):
    """Schema model class for registration information."""

    token: Optional[str] = None


class RegistrationUpdate(BaseModel):
    """Schema model class for registration update."""

    status: RegistrationStatusEnum
