from typing import Optional

from pydantic import BaseModel, Field, model_validator


class PileInput(BaseModel):
    pile_count: int
    pile_diameter_m: float
    pile_length_m: float
    reserve_percent: Optional[float] = Field(default=10, ge=0, le=100)
    rebar_kg_per_m3: Optional[float] = Field(default=None, ge=0)

    @model_validator(mode="after")
    def check_values(self):
        if self.pile_count <= 0:
            raise ValueError("pile_count must be greater than 0")
        if self.pile_diameter_m <= 0:
            raise ValueError("pile_diameter_m must be greater than 0")
        if self.pile_length_m <= 0:
            raise ValueError("pile_length_m must be greater than 0")
        return self


class CushionInput(BaseModel):
    length_m: float
    width_m: float
    sand_thickness_m: Optional[float] = Field(default=0, ge=0)
    gravel_thickness_m: Optional[float] = Field(default=0, ge=0)
    geotextile_overlap_percent: Optional[float] = Field(default=None, ge=0, le=100)
    waste_percent: Optional[float] = Field(default=0, ge=0, le=100)

    @model_validator(mode="after")
    def check_values(self):
        if self.length_m <= 0:
            raise ValueError("length_m must be greater than 0")
        if self.width_m <= 0:
            raise ValueError("width_m must be greater than 0")
        if (self.sand_thickness_m or 0) <= 0 and (self.gravel_thickness_m or 0) <= 0:
            raise ValueError("at least one of sand_thickness_m or gravel_thickness_m must be greater than 0")
        return self


class FoundationWaterproofingInput(BaseModel):
    surface_area_m2: Optional[float] = Field(default=None, gt=0)
    length_m: Optional[float] = Field(default=None, gt=0)
    width_m: Optional[float] = Field(default=None, gt=0)
    height_m: Optional[float] = Field(default=None, gt=0)
    layers_count: int = Field(default=1)
    overlap_percent: Optional[float] = Field(default=0, ge=0, le=100)
    waste_percent: Optional[float] = Field(default=0, ge=0, le=100)
    primer_coverage_m2_per_l: Optional[float] = Field(default=None, gt=0)

    @model_validator(mode="after")
    def check_values(self):
        if self.layers_count <= 0:
            raise ValueError("layers_count must be greater than 0")
        if self.surface_area_m2 is None:
            if self.length_m is None or self.width_m is None or self.height_m is None:
                raise ValueError(
                    "provide surface_area_m2 or all of length_m, width_m and height_m"
                )
        return self

    def base_area_m2(self) -> float:
        if self.surface_area_m2 is not None:
            return self.surface_area_m2
        perimeter = 2 * (self.length_m + self.width_m)
        return perimeter * self.height_m


class FoundationInsulationInput(BaseModel):
    area_m2: float
    insulation_thickness_mm: float
    board_length_m: Optional[float] = Field(default=None, gt=0)
    board_width_m: Optional[float] = Field(default=None, gt=0)
    adhesive_coverage_m2_per_bag: Optional[float] = Field(default=None, gt=0)
    waste_percent: Optional[float] = Field(default=0, ge=0, le=100)

    @model_validator(mode="after")
    def check_values(self):
        if self.area_m2 <= 0:
            raise ValueError("area_m2 must be greater than 0")
        if self.insulation_thickness_mm <= 0:
            raise ValueError("insulation_thickness_mm must be greater than 0")
        return self
