from typing import Any, Optional, Literal

from pydantic import BaseModel, Field


class CalculationStep(BaseModel):
    label: str
    formula: Optional[str] = None
    input_values: dict[str, Any] = Field(default_factory=dict)
    result: float
    unit: str


class MaterialItem(BaseModel):
    name: str = Field(..., min_length=1)
    quantity: float = Field(..., ge=0)
    unit: str = Field(..., min_length=1)
    waste_percent: Optional[float] = Field(default=None, ge=0)


class CalculationAssumption(BaseModel):
    key: str
    description: str
    source: Optional[str] = None


class CalculationWarning(BaseModel):
    code: str
    message: str
    severity: Literal["info", "warning", "error"] = "warning"


class CalculationResult(BaseModel):
    calculation_type: str
    steps: list[CalculationStep] = Field(default_factory=list)
    materials: list[MaterialItem] = Field(default_factory=list)
    assumptions: list[CalculationAssumption] = Field(default_factory=list)
    warnings: list[CalculationWarning] = Field(default_factory=list)