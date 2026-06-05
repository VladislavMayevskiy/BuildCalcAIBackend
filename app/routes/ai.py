"""Compatibility shim.

This module remains to avoid breaking imports of `app.routes.ai`.
The canonical route module is `app.api.routes.ai`.
"""

from app.api.routes.ai import router  # noqa: F401
