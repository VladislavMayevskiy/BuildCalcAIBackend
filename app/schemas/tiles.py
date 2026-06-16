from typing import Optional

from pydantic import BaseModel, Field, model_validator


class TilesFloorInput(BaseModel):
    area_m2: float
    tile_length_m: float
    tile_width_m: float
    waste_percent: Optional[float] = Field(default=10, ge=0, le=100)
    adhesive_kg_per_m2: Optional[float] = Field(default=None, ge=0)
    grout_kg_per_m2: Optional[float] = Field(default=None, ge=0)
    pack_area_m2: Optional[float] = Field(default=None, gt=0)

    @model_validator(mode="after")
    def check_values(self):
        if self.area_m2 <= 0:
            raise ValueError("area_m2 must be greater than 0")
        if self.tile_length_m <= 0:
            raise ValueError("tile_length_m must be greater than 0")
        if self.tile_width_m <= 0:
            raise ValueError("tile_width_m must be greater than 0")
        return self


class TilesWallInput(BaseModel):
    gross_area_m2: float
    tile_length_m: float
    tile_width_m: float
    openings_area_m2: Optional[float] = Field(default=0, ge=0)
    waste_percent: Optional[float] = Field(default=10, ge=0, le=100)
    adhesive_kg_per_m2: Optional[float] = Field(default=None, ge=0)
    grout_kg_per_m2: Optional[float] = Field(default=None, ge=0)
    pack_area_m2: Optional[float] = Field(default=None, gt=0)

    @model_validator(mode="after")
    def check_values(self):
        if self.gross_area_m2 <= 0:
            raise ValueError("gross_area_m2 must be greater than 0")
        if self.tile_length_m <= 0:
            raise ValueError("tile_length_m must be greater than 0")
        if self.tile_width_m <= 0:
            raise ValueError("tile_width_m must be greater than 0")
        return self


class TilesAdhesiveInput(BaseModel):
    area_m2: float
    adhesive_kg_per_m2: float = Field(..., gt=0)
    bag_weight_kg: float = Field(..., gt=0)
    waste_percent: Optional[float] = Field(default=5, ge=0, le=100)

    @model_validator(mode="after")
    def check_values(self):
        if self.area_m2 <= 0:
            raise ValueError("area_m2 must be greater than 0")
        return self


class TilesGroutInput(BaseModel):
    area_m2: float
    grout_kg_per_m2: float = Field(..., gt=0)
    bag_weight_kg: Optional[float] = Field(default=None, gt=0)
    waste_percent: Optional[float] = Field(default=5, ge=0, le=100)

    @model_validator(mode="after")
    def check_values(self):
        if self.area_m2 <= 0:
            raise ValueError("area_m2 must be greater than 0")
        return self
