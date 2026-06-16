from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, model_validator


class HeatLossSurface(BaseModel):
    area_m2: float = Field(..., gt=0)
    u_value_w_m2k: float = Field(..., gt=0)


class HeatLossBasicInput(BaseModel):
    surfaces: list[HeatLossSurface] = Field(..., min_length=1)
    delta_t_k: float
    air_volume_m3: Optional[float] = Field(default=None, gt=0)
    air_change_rate_h: Optional[float] = Field(default=None, ge=0)

    @model_validator(mode="after")
    def check_values(self):
        if self.delta_t_k <= 0:
            raise ValueError("delta_t_k must be greater than 0")
        return self


class PhaseType(str, Enum):
    single_phase = "single_phase"
    three_phase = "three_phase"


class ElectricalLoad(BaseModel):
    name: str = Field(..., min_length=1)
    power_kw: float = Field(..., ge=0)
    demand_factor: float = Field(default=1.0, gt=0, le=1)


class ElectricalLoadBasicInput(BaseModel):
    loads: list[ElectricalLoad] = Field(..., min_length=1)
    voltage_v: float = Field(..., gt=0)
    phase_type: PhaseType
    power_factor: Optional[float] = Field(default=0.9, gt=0, le=1)


class PipeRun(BaseModel):
    length_m: float = Field(..., gt=0)
    inner_diameter_mm: float = Field(..., gt=0)


class PipeVolumeInput(BaseModel):
    pipe_runs: list[PipeRun] = Field(..., min_length=1)
