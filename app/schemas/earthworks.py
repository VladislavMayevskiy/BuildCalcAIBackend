from typing import Optional

from pydantic import BaseModel, Field, model_validator


class ExcavationInput(BaseModel):
    length_m: float
    width_m: float
    depth_m: float
    slope_allowance_percent: Optional[float] = Field(default=0, ge=0, le=200)
    bulking_percent: Optional[float] = Field(default=0, ge=0, le=200)
    backfill_percent: Optional[float] = Field(default=0, ge=0, le=100)
    waste_percent: Optional[float] = Field(default=0, ge=0, le=100)

    @model_validator(mode="after")
    def check_values(self):
        if self.length_m <= 0:
            raise ValueError("length_m must be greater than 0")
        if self.width_m <= 0:
            raise ValueError("width_m must be greater than 0")
        if self.depth_m <= 0:
            raise ValueError("depth_m must be greater than 0")
        return self


class TrenchInput(BaseModel):
    trench_length_m: float
    trench_width_m: float
    trench_depth_m: float
    bedding_thickness_m: Optional[float] = Field(default=0, ge=0)
    pipe_zone_height_m: Optional[float] = Field(default=0, ge=0)
    bulking_percent: Optional[float] = Field(default=0, ge=0, le=200)

    @model_validator(mode="after")
    def check_values(self):
        if self.trench_length_m <= 0:
            raise ValueError("trench_length_m must be greater than 0")
        if self.trench_width_m <= 0:
            raise ValueError("trench_width_m must be greater than 0")
        if self.trench_depth_m <= 0:
            raise ValueError("trench_depth_m must be greater than 0")
        return self


class BackfillInput(BaseModel):
    area_m2: float
    compacted_thickness_m: float
    compaction_factor: Optional[float] = Field(default=1.15, gt=0)
    layer_thickness_m: Optional[float] = Field(default=None, gt=0)
    waste_percent: Optional[float] = Field(default=0, ge=0, le=100)

    @model_validator(mode="after")
    def check_values(self):
        if self.area_m2 <= 0:
            raise ValueError("area_m2 must be greater than 0")
        if self.compacted_thickness_m <= 0:
            raise ValueError("compacted_thickness_m must be greater than 0")
        return self
