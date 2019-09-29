"""Manager messages collection."""
from typing import List

from yog_sothoth import schemas
from yog_sothoth.utils.project import get_app_base_url


def salutation(*, html: bool = False) -> List[str]:
    """Get the salutation message parts for the managers."""
    if html:
        return []
    return [
        f'Dear Gate Keepers:',
        f'',
    ]


def curl_registration_status(rid: str, manager_token: str,
                             *, html: bool = False) -> List[str]:
    """Get the registration status instructions message parts for the managers."""
    # ToDo: get API URL programmatically
    if html:
        return []
    return [
        f'  To check this registration request information:',
        f'      * Open your terminal and type:',
        f'          curl \\',
        f'              -X GET \\',
        f'              -u {rid}:{manager_token} \\',
        f'              -H "Accept: application/json" \\',
        f'              "{get_app_base_url()}/v1/registrations/{rid}/"',
        f'',
    ]


def curl_change_registration_status(rid: str, manager_token: str,
                                    *, html: bool = False) -> List[str]:
    """Get instructions to change registration status message parts for the managers."""
    # ToDo: get API URL programmatically
    if html:
        return []
    return [
        f'  To change this registration status (approve or reject):',
        f'      * Open your terminal and type:',
        f'          curl \\',
        f'              -X PUT \\',
        f'              -u {rid}:{manager_token} \\',
        f'              -H "Accept: application/json" \\',
        f'              -H "Content-Type: application/json" \\',
        f'              -d "{{\\"status\\": \\"<options>\\"}}" \\',
        f'              "{get_app_base_url()}/v1/registrations/{rid}/"',
        f'',
        f'          Options: {schemas.RegistrationStatusUpdateEnum.approved}'  # no comma
        f' | {schemas.RegistrationStatusUpdateEnum.rejected}',
        f'',
    ]
