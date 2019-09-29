"""Handle Matrix account creation."""
import hashlib
import hmac
from dataclasses import dataclass
from dataclasses import field
from typing import NamedTuple
from typing import Optional
from typing import Union

from yog_sothoth.conf import settings
from yog_sothoth.objects import Registration
from yog_sothoth.utils.connectors import JSONConnectorAsync


class MatrixError(Exception):
    """Matrix base exception."""


class MatrixRequestError(MatrixError):
    """Matrix request error."""


class MatrixResponseError(MatrixError):
    """Matrix response error."""


class MatrixAccount(NamedTuple):
    """Matrix account object after being created."""

    user_id: str
    home_server: str


@dataclass
class Matrix:
    """Handle Matrix account creation."""

    API_VERSION_URL_PATH = '/_matrix/client/versions'
    REGISTRATION_CLIENT_URL_PATH = '/_matrix/client/{v}/register'
    REGISTRATION_ADMIN_URL_PATH = '/_matrix/client/{v}/admin/register'
    SUPPORTED_API_VERSIONS = ('r0.5.0',)

    server_url: str
    registration: Registration
    timeout: Union[int, float]
    registration_shared_secret: Optional[str] = None
    _api_version: str = field(default='', init=False)

    def _generate_mac(self, *, nonce: str, username: str, password: str,
                      admin: bool = False, user_type: Optional[str] = None):
        """Generate MAC for the Shared-Secret registration API."""
        # This code was copied from:
        # https://github.com/matrix-org/synapse/blob/master/docs/admin_api/register_api.rst
        # See also:
        # https://github.com/matrix-org/synapse/blob/master/synapse/_scripts/register_new_matrix_user.py
        mac = hmac.new(
            key=self.registration_shared_secret.encode('utf8'),
            digestmod=hashlib.sha1,
        )
        mac.update(nonce.encode('utf8'))
        mac.update(b'\x00')
        mac.update(username.encode('utf8'))
        mac.update(b'\x00')
        mac.update(password.encode('utf8'))
        mac.update(b'\x00')
        mac.update(b'admin' if admin else b'notadmin')
        if user_type:
            mac.update(b'\x00')
            mac.update(user_type.encode('utf8'))
        return mac.hexdigest()

    async def build_url(self, path: str) -> str:
        """Build a Matrix API URL from the given path, automatically setting version."""
        url = f'{self.server_url}{path}'
        versioned = '{v}' in path
        if versioned:
            return url.format(v=await self.api_version)
        return url

    @property
    async def api_version(self) -> str:
        """Get latest API version from server (will only query once and store result)."""
        if self._api_version:
            return self._api_version

        url = await self.build_url(self.API_VERSION_URL_PATH)
        version_data, error = await JSONConnectorAsync.get(url, timeout=self.timeout)
        if error or not version_data:
            raise MatrixRequestError('Could not get API version from server')

        try:
            version: str = version_data['versions'].pop()  # KeyError, IndexError
            major, minor, patch = version.split('.')  # ValueError
        except (KeyError, IndexError, ValueError):
            raise MatrixResponseError(f'Malformed version data: {version_data}')

        # ToDo: maybe loop over versions?
        if version not in self.SUPPORTED_API_VERSIONS:
            raise MatrixError('Unsupported Matrix API version (this app needs an '
                              'update)')
        self._api_version = major
        return major

    async def create_account(self) -> MatrixAccount:
        """Create a Matrix account automatically choosing the registration API.

        This means that if the `registration_shared_secret` is set will use the
        administration API instead of the regular registration API.
        """
        if self.registration_shared_secret:
            return await self.create_account_using_shared_secret()
        return await self.create_account_using_shared_secret()

    async def create_account_using_shared_secret(self) -> MatrixAccount:
        """Create a Matrix account using the Shared-Secret API.

        See:
        https://github.com/matrix-org/synapse/blob/master/docs/admin_api/register_api.rst
        https://github.com/matrix-org/synapse/blob/master/synapse/_scripts/register_new_matrix_user.py

        :return: A dict with the "user_id" being the Matrix account user and
                 "home_server" the hostname of the home server.
        """
        url = await self.build_url(self.REGISTRATION_ADMIN_URL_PATH)
        nonce_data, error = await JSONConnectorAsync.get(url, timeout=self.timeout)
        if error or not nonce_data:
            raise MatrixRequestError('Could not get registration nonce from server')

        try:
            nonce: str = nonce_data['nonce']
        except KeyError:
            raise MatrixResponseError(f'Malformed nonce data: {nonce_data}')

        base_payload = {
            'nonce': nonce,
            'username': self.registration.username,
            'password': self.registration.password,
            'admin': False,  # Hardcoded as NOT admin. CHANGING THIS IS DANGEROUS.
            'user_type': None,  # I've no clue on what this is.
        }
        payload = {
            'mac': self._generate_mac(**base_payload),
            # This setting prevents us from getting an access_token and device_id.
            # This is important so as to not leave a device in the user's account,
            # and also because this data could access the entire user's account.
            # See:
            # https://github.com/matrix-org/matrix-doc/blob/2d784d93ef4827cf340aa1a0aa5ebb6e2bc40861/api/client-server/registration.yaml#L121
            # From our attempts, this value seems not to be part of the MAC, but it
            # works! So far we can say that Matrix/Synapse has one of the worst docs
            # ever.
            'inhibit_login': True,
        }
        payload.update(base_payload)
        result_data, error = await JSONConnectorAsync.post(
            url,
            payload,
            timeout=settings.REQUESTS_TIMEOUT,
        )
        if error or not result_data:
            raise MatrixRequestError('Could not post registration to server')

        try:
            account = MatrixAccount(**result_data)
        except TypeError:
            raise MatrixResponseError('Unexpected response after creating an account '
                                      '(it is very likely that the account has been '
                                      'created)')

        return account

    async def create_account_standard(self) -> MatrixAccount:
        """Create a Matrix account using the standard client API.

        See:
        https://matrix.org/docs/guides/client-server-api#accounts
        https://github.com/matrix-org/matrix-doc/blob/master/api/client-server/registration.yaml
        """
        # ToDo
        # For what we could see, after sending the registration POST a list of
        # following steps is returned that need to be completed for a registration
        # to be done. This is not an immediately easy thing to do and requires lots
        # of coding (or perhaps using an existing Matrix python library?) and
        # documentation and protocol reading.
        raise MatrixError('Not implemented yet')
