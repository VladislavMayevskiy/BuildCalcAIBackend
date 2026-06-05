from pydantic import BaseModel, Field
from typing import Optional

from app.schemas.calculation_result import (
    MaterialItem,
    CalculationAssumption,
    CalculationWarning,
)


class EstimateMaterialItem(MaterialItem):
    unit_price: Optional[float] = Field(default=None, ge=0)
    total_price: Optional[float] = Field(default=None, ge=0)


class EstimateResult(BaseModel):
    materials: list[EstimateMaterialItem]
    subtotal_materials: float = Field(..., ge=0)
    currency: str = Field(default="UAH", min_length=1)
    assumptions: list[CalculationAssumption] = Field(default_factory=list)
    warnings: list[CalculationWarning] = Field(default_factory=list)