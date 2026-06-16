from pydantic import BaseModel, Field
from typing import Optional

from app.schemas.calculation_result import (
    CalculationResult,
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


class AggregatedMaterialItem(BaseModel):
    name: str
    unit: str
    category: Optional[str] = None
    total_quantity: float = Field(..., ge=0)
    sources: list[str] = Field(default_factory=list)
    unit_price: Optional[float] = Field(default=None, ge=0)
    total_price: Optional[float] = Field(default=None, ge=0)


class MaterialAggregationResult(BaseModel):
    materials: list[AggregatedMaterialItem] = Field(default_factory=list)
    subtotal_materials: Optional[float] = Field(default=None, ge=0)
    currency: str = Field(default="UAH", min_length=1)
    assumptions: list[CalculationAssumption] = Field(default_factory=list)
    warnings: list[CalculationWarning] = Field(default_factory=list)


class AggregateMaterialsInput(BaseModel):
    calculations: list[CalculationResult] = Field(..., min_length=1)


class FromCalculationsInput(BaseModel):
    calculation_ids: list[int] = Field(..., min_length=1)