from typing import Optional

from pydantic import BaseModel, Field, model_validator


class FacadePanel(BaseModel):
    width_m: float = Field(..., gt=0)
    height_m: float = Field(..., gt=0)


class FacadeAreaInput(BaseModel):
    facades: list[FacadePanel] = Field(..., min_length=1)
    openings_area_m2: Optional[float] = Field(default=0, ge=0)
    waste_percent: Optional[float] = Field(default=5, ge=0, le=100)

    def gross_area_m2(self) -> float:
        return sum(panel.width_m * panel.height_m for panel in self.facades)


class FacadeInsulationInput(BaseModel):
    area_m2: float
    board_length_m: float = Field(..., gt=0)
    board_width_m: float = Field(..., gt=0)
    adhesive_coverage_m2_per_bag: Optional[float] = Field(default=None, gt=0)
    dowels_per_m2: Optional[float] = Field(default=None, ge=0)
    mesh_overlap_percent: Optional[float] = Field(default=None, ge=0, le=100)
    waste_percent: Optional[float] = Field(default=5, ge=0, le=100)

    @model_validator(mode="after")
    def check_values(self):
        if self.area_m2 <= 0:
            raise ValueError("area_m2 must be greater than 0")
        return self


class FacadePlasterInput(BaseModel):
    area_m2: float
    plaster_kg_per_m2: float = Field(..., gt=0)
    primer_coverage_m2_per_l: Optional[float] = Field(default=None, gt=0)
    waste_percent: Optional[float] = Field(default=5, ge=0, le=100)

    @model_validator(mode="after")
    def check_values(self):
        if self.area_m2 <= 0:
            raise ValueError("area_m2 must be greater than 0")
        return self


class FacadePaintInput(BaseModel):
    area_m2: float
    paint_coverage_m2_per_l: float = Field(..., gt=0)
    coats_count: int = Field(default=2, gt=0)
    primer_coverage_m2_per_l: Optional[float] = Field(default=None, gt=0)
    waste_percent: Optional[float] = Field(default=5, ge=0, le=100)

    @model_validator(mode="after")
    def check_values(self):
        if self.area_m2 <= 0:
            raise ValueError("area_m2 must be greater than 0")
        return self
