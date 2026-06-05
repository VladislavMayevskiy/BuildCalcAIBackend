"""Compatibility shim.

This module remains to avoid breaking imports of `app.routes.foundation`.
The canonical route module is `app.api.routes.foundation`.
"""

from app.api.routes.foundation import router  # noqa: F401
