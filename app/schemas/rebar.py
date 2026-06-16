from typing import Optional

from pydantic import BaseModel, Field, model_validator


class RebarLinearInput(BaseModel):
    """Input for the deterministic linear rebar calculator.

    Provide the run length either as a single ``total_length_m`` or as a list of
    ``segment_lengths_m`` (they are summed). The lap/overlap allowance can be
    given either as an absolute ``lap_length_m`` per bar or as ``lap_percent`` of
    the total bar length. If neither lap value is provided, no lap is added.
    """

    total_length_m: Optional[float] = Field(default=None)
    segment_lengths_m: Optional[list[float]] = Field(default=None)
    bar_diameter_mm: float
    bar_count: int
    lap_length_m: Optional[float] = Field(default=None)
    lap_percent: Optional[float] = Field(default=None)
    waste_percent: float = Field(default=5, ge=0, le=100)

    @model_validator(mode="after")
    def check_values(self):
        if self.total_length_m is None and not self.segment_lengths_m:
            raise ValueError("either total_length_m or segment_lengths_m must be provided")
        if self.total_length_m is not None and self.total_length_m <= 0:
            raise ValueError("total_length_m must be greater than 0")
        if self.segment_lengths_m is not None:
            if any(length <= 0 for length in self.segment_lengths_m):
                raise ValueError("all segment lengths must be greater than 0")
        if self.bar_diameter_mm <= 0:
            raise ValueError("bar_diameter_mm must be greater than 0")
        if self.bar_count <= 0:
            raise ValueError("bar_count must be greater than 0")
        if self.lap_length_m is not None and self.lap_length_m < 0:
            raise ValueError("lap_length_m cannot be negative")
        if self.lap_percent is not None and self.lap_percent < 0:
            raise ValueError("lap_percent cannot be negative")
        return self

    def length_per_bar_m(self) -> float:
        if self.total_length_m is not None:
            return self.total_length_m
        return sum(self.segment_lengths_m or [])


class RebarMeshInput(BaseModel):
    area_m2: float
    sheet_length_m: float
    sheet_width_m: float
    overlap_percent: Optional[float] = Field(default=0, ge=0, le=100)
    waste_percent: Optional[float] = Field(default=0, ge=0, le=100)
    kg_per_m2: Optional[float] = Field(default=None, ge=0)

    @model_validator(mode="after")
    def check_values(self):
        if self.area_m2 <= 0:
            raise ValueError("area_m2 must be greater than 0")
        if self.sheet_length_m <= 0:
            raise ValueError("sheet_length_m must be greater than 0")
        if self.sheet_width_m <= 0:
            raise ValueError("sheet_width_m must be greater than 0")
        return self


class RebarStirrupsInput(BaseModel):
    beam_length_m: float
    spacing_m: float
    stirrup_width_m: float
    stirrup_height_m: float
    bar_diameter_mm: float
    hook_length_m: Optional[float] = Field(default=0, ge=0)
    waste_percent: Optional[float] = Field(default=0, ge=0, le=100)

    @model_validator(mode="after")
    def check_values(self):
        if self.beam_length_m <= 0:
            raise ValueError("beam_length_m must be greater than 0")
        if self.spacing_m <= 0:
            raise ValueError("spacing_m must be greater than 0")
        if self.stirrup_width_m <= 0:
            raise ValueError("stirrup_width_m must be greater than 0")
        if self.stirrup_height_m <= 0:
            raise ValueError("stirrup_height_m must be greater than 0")
        if self.bar_diameter_mm <= 0:
            raise ValueError("bar_diameter_mm must be greater than 0")
        return self


class RebarLapLengthInput(BaseModel):
    bar_diameter_mm: float
    bar_count: int
    lap_multiplier: Optional[float] = Field(default=40, gt=0)
    laps_per_bar: Optional[int] = Field(default=1, ge=0)

    @model_validator(mode="after")
    def check_values(self):
        if self.bar_diameter_mm <= 0:
            raise ValueError("bar_diameter_mm must be greater than 0")
        if self.bar_count <= 0:
            raise ValueError("bar_count must be greater than 0")
        return self
