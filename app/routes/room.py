"""Compatibility shim.

This module remains to avoid breaking imports of `app.routes.room`.
The canonical route module is `app.api.routes.rooms`.
"""

from app.api.routes.rooms import router  # noqa: F401