from app.schemas.ai import (AIParsedParameter)



UNIT_TO_METERS = {
    "m": 1.0,
    "cm": 0.01,
    "mm": 0.001,
}


def convert_to_meters(parameter: AIParsedParameter) -> float:
    if parameter.value is None:
        raise ValueError(
            f"Parameter '{parameter.name}' has no value"
        )

    if isinstance(parameter.value, bool):
        raise ValueError(
            f"Parameter '{parameter.name}' must be numeric"
        )

    try:
        value = float(parameter.value)
    except (TypeError, ValueError) as error:
        raise ValueError(
            f"Parameter '{parameter.name}' must be numeric"
        ) from error

    if value <= 0:
        raise ValueError(
            f"Parameter '{parameter.name}' must be greater than zero"
        )

    if parameter.unit not in UNIT_TO_METERS:
        raise ValueError(
            f"Unsupported unit '{parameter.unit}' "
            f"for '{parameter.name}'"
        )

    return value * UNIT_TO_METERS[parameter.unit]

