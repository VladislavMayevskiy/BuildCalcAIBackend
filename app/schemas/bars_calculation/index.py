from pydantic import BaseModel, model_validator

class BarsCalculationInput(BaseModel):
    quantity: int
    length_per_bar_m: float
    diameter_mm: int 
    reserve_percent: int
    @model_validator(mode="after")
    def check_dimensions(self):
        if self.quantity <= 0:
            raise ValueError("quantity must be greater than 0")
        if self.length_per_bar_m <= 0:
            raise ValueError("length per bar must be greater than 0")
        if self.diameter_mm <= 0:
            raise ValueError("diameter must be greater than 0")
        if self.reserve_percent < 0 or self.reserve_percent > 100:
            raise ValueError("reserve_percent must be between 0 and 100")
        return self
    


class BarsCalculationResponse(BaseModel):
    overall_length_m: float
    overall_weight_kg: float
    weight_per_bar_kg: float
    weight_per_meter_kg: float
    overall_length_with_reserve_m: float
    overall_weight_with_reserve_kg: float
    reserve_multiplier: float

