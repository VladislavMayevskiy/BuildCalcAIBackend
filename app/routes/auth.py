"""Compatibility shim.

This module remains to avoid breaking imports of `app.routes.auth`.
The canonical route module is `app.api.routes.auth`.
"""

from app.api.routes.auth import router  # noqa: F401