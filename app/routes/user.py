"""Compatibility shim.

This module remains to avoid breaking imports of `app.routes.user`.
The canonical route module is `app.api.routes.users`.
"""

from app.api.routes.users import router  # noqa: F401