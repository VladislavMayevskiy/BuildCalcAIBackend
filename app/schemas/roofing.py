from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, model_validator


class RoofType(str, Enum):
    gable = "gable"
    hip = "hip"
    mono = "mono"
    flat = "flat"


class RoofAreaInput(BaseModel):
    length_m: float
    width_m: float
    slope_degrees: Optional[float] = Field(default=None, ge=0, lt=90)
    slope_percent: Optional[float] = Field(default=None, ge=0)
    roof_type: Optional[RoofType] = Field(default=None)
    waste_percent: Optional[float] = Field(default=5, ge=0, le=100)

    @model_validator(mode="after")
    def check_values(self):
        if self.length_m <= 0:
            raise ValueError("length_m must be greater than 0")
        if self.width_m <= 0:
            raise ValueError("width_m must be greater than 0")
        if self.slope_degrees is None and self.slope_percent is None:
            raise ValueError("provide slope_degrees or slope_percent")
        return self


class RoofCoveringInput(BaseModel):
    roof_area_m2: float
    sheet_length_m: Optional[float] = Field(default=None, gt=0)
    sheet_width_m: Optional[float] = Field(default=None, gt=0)
    overlap_percent: Optional[float] = Field(default=0, ge=0, le=100)
    fasteners_per_m2: Optional[float] = Field(default=None, ge=0)
    waste_percent: Optional[float] = Field(default=5, ge=0, le=100)

    @model_validator(mode="after")
    def check_values(self):
        if self.roof_area_m2 <= 0:
            raise ValueError("roof_area_m2 must be greater than 0")
        return self


class RoofMembraneInput(BaseModel):
    roof_area_m2: float
    roll_area_m2: Optional[float] = Field(default=None, gt=0)
    overlap_percent: Optional[float] = Field(default=10, ge=0, le=100)
    waste_percent: Optional[float] = Field(default=5, ge=0, le=100)

    @model_validator(mode="after")
    def check_values(self):
        if self.roof_area_m2 <= 0:
            raise ValueError("roof_area_m2 must be greater than 0")
        return self


class RoofInsulationInput(BaseModel):
    roof_area_m2: float
    thickness_mm: float
    board_length_m: Optional[float] = Field(default=None, gt=0)
    board_width_m: Optional[float] = Field(default=None, gt=0)
    waste_percent: Optional[float] = Field(default=5, ge=0, le=100)

    @model_validator(mode="after")
    def check_values(self):
        if self.roof_area_m2 <= 0:
            raise ValueError("roof_area_m2 must be greater than 0")
        if self.thickness_mm <= 0:
            raise ValueError("thickness_mm must be greater than 0")
        return self


class RoofGuttersInput(BaseModel):
    eaves_length_m: float
    downpipe_spacing_m: Optional[float] = Field(default=10, gt=0)
    corners_count: Optional[int] = Field(default=0, ge=0)
    waste_percent: Optional[float] = Field(default=5, ge=0, le=100)

    @model_validator(mode="after")
    def check_values(self):
        if self.eaves_length_m <= 0:
            raise ValueError("eaves_length_m must be greater than 0")
        return self
