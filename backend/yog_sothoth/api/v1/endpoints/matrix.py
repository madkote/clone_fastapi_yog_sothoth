"""Fake Matrix endpoint for development and testing."""
from fastapi import APIRouter

router = APIRouter()


@router.get('/_matrix/client/versions')
async def fake_matrix_api_version():
    """Fake get Matrix API version."""
    return {'versions': ['r0.5.0']}


@router.get('/_matrix/client/r0/admin/register')
async def fake_matrix_registration_nonce():
    """Fake get Matrix account registration nonce."""
    return {'nonce': 'somenonce'}


@router.post('/_matrix/client/r0/admin/register')
async def fake_matrix_registration_request():
    """Fake Matrix account creation."""
    return {'user_id': '@fake:home.server', 'home_server': 'home.server'}
