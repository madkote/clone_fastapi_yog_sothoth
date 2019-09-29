"""User messages collection."""
from typing import List

from yog_sothoth import schemas
from yog_sothoth.utils.project import get_app_base_url


def salutation(username: str, *, html: bool = False) -> List[str]:
    """Get the salutation message parts for a user."""
    if html:
        return []
    return [
        f'Dear {username}:',
        f'',
    ]


def registration_information(rid: str, token: str,
                             *, html: bool = False) -> List[str]:
    """Get the registration information message parts."""
    if html:
        return []
    return [
        f'  Here is the information you need to know:',
        f'      * **registration id**:  {rid}',
        f'      * **token**:            {token}',
        f'',
        f'  If you did not apply for this registration, please **delete it now**.',
        f'',
    ]


def curl_registration_status(rid: str, token: str, *, html: bool = False) -> List[str]:
    """Get the registration status instructions message parts for a user."""
    # ToDo: get API URL programmatically
    if html:
        return []
    return [
        f'  To check your registration request information:',
        f'      * Open your terminal and type:',
        f'          curl \\',
        f'              -X GET \\',
        f'              -u {rid}:{token} \\',
        f'              -H "Accept: application/json" \\',
        f'              "{get_app_base_url()}/v1/registrations/{rid}/"',
        f'',
    ]


def curl_delete_registration(rid: str, token: str, *, html: bool = False) -> List[str]:
    """Get the registration deletion message parts for the user."""
    if html:
        return []
    return [
        f'  To delete your registration request:',
        f'      * Open your terminal and type:',
        f'          curl \\',
        f'              -X DELETE \\',
        f'              -u {rid}:{token} \\',
        f'              -H "Accept: application/json" \\',
        f'              "{get_app_base_url()}/v1/registrations/{rid}/"',
        f'',
    ]


def status_approved(rid: str, token: str, *, html: bool = False) -> List[str]:
    """Get the status approved message parts for the user."""
    if html:
        return []
    return [
        f'  **IMPORTANT**:',
        f'  To finish your registration request and **create your Matrix '  # no comma
        f'account**, send the **username** you want to have:',
        f'      * Open your terminal and type:',
        f'          curl \\',
        f'              -X PATCH \\',
        f'              -u {rid}:{token} \\',
        f'              -H "Accept: application/json" \\',
        f'              -H "Content-Type: application/json" \\',
        f'              -d "{{\\"matrix_status\\": '  # no comma
        f'\\"{schemas.MatrixRegStatusUpdateEnum.processing}\\", '  # no comma
        f'\\"username\\": \\"<username>\\"}}" \\',
        f'              "{get_app_base_url()}/v1/registrations/{rid}/"',
        f'',
    ]


def matrix_account_created(user_id: str, home_server: str,
                           *, html: bool = False) -> List[str]:
    """Get the matrix account created message parts for the user."""
    if html:
        return []
    return [
        f'  Here is your Matrix account user identifier for {home_server}:',
        f'  {user_id}',
        f'',
    ]
