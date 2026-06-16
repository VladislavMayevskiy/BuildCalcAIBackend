from typing import Optional

from pydantic import BaseModel, Field, model_validator


class WallBlocksInput(BaseModel):
    wall_length_m: float
    wall_height_m: float
    block_length_m: float
    block_height_m: float
    openings_area_m2: Optional[float] = Field(default=0, ge=0)
    block_width_m: Optional[float] = Field(default=None, gt=0)
    joint_thickness_m: Optional[float] = Field(default=0.01, ge=0)
    waste_percent: Optional[float] = Field(default=5, ge=0, le=100)
    mortar_kg_per_m2: Optional[float] = Field(default=None, ge=0)

    @model_validator(mode="after")
    def check_values(self):
        if self.wall_length_m <= 0:
            raise ValueError("wall_length_m must be greater than 0")
        if self.wall_height_m <= 0:
            raise ValueError("wall_height_m must be greater than 0")
        if self.block_length_m <= 0:
            raise ValueError("block_length_m must be greater than 0")
        if self.block_height_m <= 0:
            raise ValueError("block_height_m must be greater than 0")
        return self


class WallBricksInput(BaseModel):
    wall_length_m: float
    wall_height_m: float
    brick_length_m: float
    brick_height_m: float
    openings_area_m2: Optional[float] = Field(default=0, ge=0)
    brick_width_m: Optional[float] = Field(default=None, gt=0)
    joint_thickness_m: Optional[float] = Field(default=0.01, ge=0)
    wall_thickness_bricks: Optional[float] = Field(default=1, gt=0)
    waste_percent: Optional[float] = Field(default=5, ge=0, le=100)

    @model_validator(mode="after")
    def check_values(self):
        if self.wall_length_m <= 0:
            raise ValueError("wall_length_m must be greater than 0")
        if self.wall_height_m <= 0:
            raise ValueError("wall_height_m must be greater than 0")
        if self.brick_length_m <= 0:
            raise ValueError("brick_length_m must be greater than 0")
        if self.brick_height_m <= 0:
            raise ValueError("brick_height_m must be greater than 0")
        return self


class WallMortarInput(BaseModel):
    masonry_area_m2: float
    wall_thickness_m: float
    mortar_rate_m3_per_m2: Optional[float] = Field(default=None, gt=0)
    joint_fraction: Optional[float] = Field(default=0.2, gt=0, le=1)
    dry_mix_kg_per_m3: Optional[float] = Field(default=1600, gt=0)
    bag_weight_kg: Optional[float] = Field(default=None, gt=0)
    waste_percent: Optional[float] = Field(default=5, ge=0, le=100)

    @model_validator(mode="after")
    def check_values(self):
        if self.masonry_area_m2 <= 0:
            raise ValueError("masonry_area_m2 must be greater than 0")
        if self.wall_thickness_m <= 0:
            raise ValueError("wall_thickness_m must be greater than 0")
        return self
