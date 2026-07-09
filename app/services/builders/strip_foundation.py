from typing import Any

from app.schemas.ai import AIParsedParameter 
from app.services.builders.converts_to_m import convert_to_meters

def build_strip_foundation_parameters(
    parameters: dict[str, AIParsedParameter],
) -> dict[str, Any]:
    required_parameters = {"width", "length", "foundation_depth", "foundation_width"}
    missing_parameters = required_parameters - parameters.keys()
    if missing_parameters:
        text = ", ".join(sorted(missing_parameters))
        raise ValueError(f"Required parameters were not returned: {text}")

    input_data = {
        "length": convert_to_meters(parameters["length"]),
        "width": convert_to_meters(parameters["width"]),
        "foundation_depth": convert_to_meters(parameters["foundation_depth"]),
        "foundation_width": convert_to_meters(parameters["foundation_width"]),
    }
    reserve_percent = parameters.get("reserve_percent")
    if reserve_percent is not None:
        value = reserve_percent.value
        if value is None:
            raise ValueError("Reserve percent not found")
        float_value = float(value)
        input_data["reserve_percent"] = float_value
        
    return input_data
    