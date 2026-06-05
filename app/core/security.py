"""Security wrapper.

The canonical implementation currently lives in `app.oauth2`.
This module exists to support the target folder structure without moving working code yet.
"""

from app.oauth2 import (  # noqa: F401
    create_acces_token,
    get_current_user,
    oauth2_scheme,
    verify_acces_token,
)

