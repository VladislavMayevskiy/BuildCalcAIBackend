from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class CalculationInput(BaseModel):
    length: float = Field(..., gt=0)
    width: float = Field(..., gt=0)
    height: float = Field(..., gt=0)
    windows_area: float = Field(default=0, ge=0)
    doors_area: float = Field(default=0, ge=0)


class CalculationResponse(BaseModel):
    floor_area: float
    ceiling_area: float
    wall_area: float
    wall_area_with_reserve: float
    paint_liters: float
    tile_required_sqm: float


class CalculationHistoryResponse(BaseModel):
    id: int
    calculation_type: str
    input_data: dict[str, Any]
    result_data: dict[str, Any]
    room_project_id: Optional[int] = None
    created_at: datetime