"""Generic messages collection."""
from typing import List


def action_new_registration(matrix_url: str, *, html: bool = False) -> List[str]:
    """Get the new registration message parts."""
    if html:
        return []
    return [
        f'  We have received a Matrix account registration request at',
        f'  {matrix_url}',
        f'',
    ]


def status_changes_repetition(*, html: bool = False) -> List[str]:
    """Get the status changes repetition message parts."""
    if html:
        return []
    return [
        f'  You will receive an email like this whenever the status of this',
        f'  registration request changes.',
        f'',
    ]


def status_changed(status: str,
                   rid: str,
                   *,
                   matrix: bool = False,
                   html: bool = False) -> List[str]:
    """Get the (matrix) status changed message parts."""
    if matrix:
        matrix_text = 'Matrix '
    else:
        matrix_text = ''
    if html:
        return []
    return [
        f'  The {matrix_text}**status** of the registration request '  # no comma
        f'**{rid}** changed to: **{status}**.',
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
    ]


def frontend_propaganda(frontend_url: str, *, html: bool = False) -> List[str]:
    """Get the frontend propaganda message parts."""
    if html:
        return []
    return [
        f'  You can do this and more in our web frontend:',
        f'  {frontend_url}',
        f'',
    ]


def contact_address(contact: str, *, html: bool = False) -> List[str]:
    """Get the contact address message parts."""
    if html:
        return []
    return [
        f'  For any questions address yourself to {contact}',
        f'',
    ]


def signature(*, html: bool = False) -> List[str]:
    """Get the signature message parts."""
    if html:
        return []
    return [
        f'  Please DO NOT reply to this email.',
        f'',
        f'Regards,',
        f'Yog-Sothoth, the key and guardian of the gate.',
        f'',
    ]
