from typing import Optional

from pydantic import BaseModel, Field, model_validator


class FloorScreedInput(BaseModel):
    area_m2: float
    thickness_m: float
    density_kg_per_m3: Optional[float] = Field(default=1800, gt=0)
    bag_weight_kg: Optional[float] = Field(default=None, gt=0)
    waste_percent: Optional[float] = Field(default=5, ge=0, le=100)

    @model_validator(mode="after")
    def check_values(self):
        if self.area_m2 <= 0:
            raise ValueError("area_m2 must be greater than 0")
        if self.thickness_m <= 0:
            raise ValueError("thickness_m must be greater than 0")
        return self


class FloorInsulationInput(BaseModel):
    area_m2: float
    thickness_mm: float
    board_length_m: Optional[float] = Field(default=None, gt=0)
    board_width_m: Optional[float] = Field(default=None, gt=0)
    waste_percent: Optional[float] = Field(default=5, ge=0, le=100)

    @model_validator(mode="after")
    def check_values(self):
        if self.area_m2 <= 0:
            raise ValueError("area_m2 must be greater than 0")
        if self.thickness_mm <= 0:
            raise ValueError("thickness_mm must be greater than 0")
        return self


class FloorLaminateInput(BaseModel):
    area_m2: float
    waste_percent: Optional[float] = Field(default=10, ge=0, le=100)
    pack_area_m2: Optional[float] = Field(default=None, gt=0)
    perimeter_m: Optional[float] = Field(default=None, gt=0)
    openings_width_m: Optional[float] = Field(default=0, ge=0)
    underlay_enabled: Optional[bool] = Field(default=True)

    @model_validator(mode="after")
    def check_values(self):
        if self.area_m2 <= 0:
            raise ValueError("area_m2 must be greater than 0")
        return self
