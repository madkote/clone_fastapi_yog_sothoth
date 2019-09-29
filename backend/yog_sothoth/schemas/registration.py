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
    """Registration status options."""

    pending = 'pending'
    approved = 'approved'
    rejected = 'rejected'
    deleted = 'deleted'


class RegistrationStatusUpdateEnum(str, Enum):
    """Registration status options for update."""

    approved = RegistrationStatusEnum.approved.value
    rejected = RegistrationStatusEnum.rejected.value


class MatrixRegStatusEnum(str, Enum):
    """Matrix account registration status options."""

    pending = 'pending'
    processing = 'processing'
    success = 'success'
    failed = 'failed'


class MatrixRegStatusUpdateEnum(str, Enum):
    """Matrix account registration status options for update."""

    processing = MatrixRegStatusEnum.processing.value


class RegistrationCreate(BaseModel):
    """Schema model class to create a new registration."""

    email: EmailStr = Schema('', max_length=140)


class RegistrationInfoReduced(BaseModel):
    """Schema model class for reduced registration information."""

    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    rid: str = Schema(..., min_length=6, max_length=6)  # 4B
    status: RegistrationStatusEnum = RegistrationStatusEnum.pending
    matrix_status: MatrixRegStatusEnum = MatrixRegStatusEnum.pending
    creation: datetime = Schema(...)
    modification: datetime = Schema(...)


class RegistrationInfo(RegistrationInfoReduced):
    """Schema model class for registration information."""

    token: Optional[str] = Schema(None, min_length=11, max_length=11)  # 8B


class RegistrationUpdateByManager(BaseModel):
    """Schema model class for registration update by manager."""

    status: RegistrationStatusUpdateEnum


class RegistrationUpdateByUser(BaseModel):
    """Schema model class for registration update by user."""

    username: str = Schema(..., min_length=4, max_length=140)
    email: EmailStr = Schema('', max_length=140)
    matrix_status: MatrixRegStatusUpdateEnum = MatrixRegStatusUpdateEnum.processing

    # noinspection PyMethodParameters
    @validator('username')
    def username_chars(cls, value) -> str:  # noqa: N805
        """Validate username characters."""
        if re.match(r'^([\w.-]+)$', value):
            return value
        raise ValueError('username can only be alphanumeric with symbols: _.-')


class RegistrationUpdateMatrixStatus(BaseModel):
    """Schema model class for matrix registration status update."""

    matrix_status: MatrixRegStatusEnum = MatrixRegStatusUpdateEnum.processing
    email: str = ''


class UserAuthBasic(BaseModel):
    """User authentication schema model for BasicAuth."""

    rid: str = Schema(..., min_length=6, max_length=6)
    token: str = Schema(..., min_length=11, max_length=11)
