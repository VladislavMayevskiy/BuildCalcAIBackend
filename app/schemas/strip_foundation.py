from pydantic import BaseModel, Field, model_validator

#Стрічковий фундамент

class StripFoundationInput(BaseModel):
    length: float
    width: float
    foundation_width: float
    foundation_depth: float
    reserve_percent: float = Field(default=10, ge=0, le=100)

    @model_validator(mode="after")
    def check_dimensions(self):
        if self.length <= 0:
            raise ValueError("length must be greater than 0")
        if self.width <= 0:
            raise ValueError("width must be greater than 0")
        if self.foundation_width <= 0:
            raise ValueError("foundation_width must be greater than 0")
        if self.foundation_depth <= 0:
            raise ValueError("foundation_depth must be greater than 0")
        return self

class StripFoundationResponse(BaseModel):
    perimeter: float
    concrete_volume: float
    concrete_volume_with_reserve: float

    