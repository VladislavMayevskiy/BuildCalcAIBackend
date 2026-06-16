from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, model_validator


class ConcreteShape(str, Enum):
    rectangular_prism = "rectangular_prism"
    slab = "slab"
    column = "column"
    beam = "beam"
    cylinder = "cylinder"


class ConcreteVolumeInput(BaseModel):
    shape_type: ConcreteShape
    length_m: Optional[float] = Field(default=None, gt=0)
    width_m: Optional[float] = Field(default=None, gt=0)
    height_m: Optional[float] = Field(default=None, gt=0)
    thickness_m: Optional[float] = Field(default=None, gt=0)
    diameter_m: Optional[float] = Field(default=None, gt=0)
    count: int = Field(default=1, gt=0)
    reserve_percent: Optional[float] = Field(default=10, ge=0, le=100)

    @model_validator(mode="after")
    def check_dimensions(self):
        required = {
            ConcreteShape.rectangular_prism: ["length_m", "width_m", "height_m"],
            ConcreteShape.beam: ["length_m", "width_m", "height_m"],
            ConcreteShape.slab: ["length_m", "width_m", "thickness_m"],
            ConcreteShape.column: ["width_m", "height_m"],
            ConcreteShape.cylinder: ["diameter_m", "height_m"],
        }[self.shape_type]
        for field_name in required:
            if getattr(self, field_name) is None:
                raise ValueError(f"{field_name} is required for shape '{self.shape_type.value}'")
        # column accepts an optional separate depth via 'length_m'; default to square if missing
        return self


class ConcreteMixInput(BaseModel):
    concrete_volume_m3: float
    mix_ratio_cement: float = Field(..., gt=0)
    mix_ratio_sand: float = Field(..., gt=0)
    mix_ratio_gravel: float = Field(..., gt=0)
    water_cement_ratio: Optional[float] = Field(default=0.5, gt=0, le=1.5)
    dry_volume_factor: Optional[float] = Field(default=1.54, gt=1, le=2)
    cement_density_kg_per_m3: Optional[float] = Field(default=1440, gt=0)
    cement_bag_weight_kg: Optional[float] = Field(default=50, gt=0)

    @model_validator(mode="after")
    def check_values(self):
        if self.concrete_volume_m3 <= 0:
            raise ValueError("concrete_volume_m3 must be greater than 0")
        return self
