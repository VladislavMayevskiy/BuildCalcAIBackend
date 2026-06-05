from pydantic import BaseModel, Field, model_validator


class SlabFoundationInput(BaseModel):
    length: float
    width: float
    slab_thickness: float
    reserve_percent: float = Field(default=10, ge=0, le=100)

    @model_validator(mode="after")
    def check_dimensions(self):
        if self.length <= 0:
            raise ValueError("length must be greater than 0")
        if self.width <= 0:
            raise ValueError("width must be greater than 0")
        if self.slab_thickness <= 0:
            raise ValueError("slab_thickness must be greater than 0")
        return self
