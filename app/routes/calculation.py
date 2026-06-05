"""Compatibility shim.

This module remains to avoid breaking imports of `app.routes.calculation`.
The canonical route module is `app.api.routes.calculations`.
"""

from app.api.routes.calculations import router  # noqa: F401