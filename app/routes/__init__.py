"""Compatibility shim.

This module remains to avoid breaking imports of `app.routes.calculation`.
The canonical route module is `app.api.routes.calculations`.
"""

from app.api.routes.bars_calculation.index import router  # noqa: F401