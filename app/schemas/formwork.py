from typing import Optional

from pydantic import BaseModel, Field, model_validator


class FormworkFoundationInput(BaseModel):
    """Input for the deterministic foundation formwork calculator.

    Formwork area is the contact area of the boards/panels against the concrete.
    For a strip foundation both inner and outer faces are usually formed, so
    ``sides_count`` defaults to 2. Optionally provide ``panel_area_m2`` to also
    get the number of boards/panels required.
    """

    perimeter_m: float
    height_m: float
    sides_count: int = Field(default=2)
    waste_percent: float = Field(default=10, ge=0, le=100)
    panel_area_m2: Optional[float] = Field(default=None)

    @model_validator(mode="after")
    def check_values(self):
        if self.perimeter_m <= 0:
            raise ValueError("perimeter_m must be greater than 0")
        if self.height_m <= 0:
            raise ValueError("height_m must be greater than 0")
        if self.sides_count <= 0:
            raise ValueError("sides_count must be greater than 0")
        if self.panel_area_m2 is not None and self.panel_area_m2 <= 0:
            raise ValueError("panel_area_m2 must be greater than 0")
        return self
