from app.schemas.strip_foundation import (
    StripFoundationInput,
    StripFoundationResponse,
)
from app.schemas.calculation_result import (
    CalculationResult,
    CalculationStep,
    CalculationAssumption,
    MaterialItem,
    CalculationWarning,
)


def calculate_strip_foundation(data: StripFoundationInput) -> StripFoundationResponse:
    perimeter = 2 * (data.width + data.length)
    concrete_volume = perimeter * data.foundation_depth * data.foundation_width
    concrete_volume_with_reserve = concrete_volume * (1 + data.reserve_percent / 100)

    return StripFoundationResponse(
        perimeter=round(perimeter, 2),
        concrete_volume=round(concrete_volume, 2),
        concrete_volume_with_reserve=round(concrete_volume_with_reserve, 2),
    )


def calculate_strip_foundation_v2(data: StripFoundationInput) -> CalculationResult:
    perimeter = round(2 * (data.width + data.length), 2)
    concrete_volume = round(
        perimeter * data.foundation_depth * data.foundation_width,
        2,
    )
    concrete_volume_with_reserve = round(
        concrete_volume * (1 + data.reserve_percent / 100),
        2,
    )

    return CalculationResult(
        calculation_type="strip_foundation",
        steps=[
            CalculationStep(
                label="Foundation perimeter",
                formula="2 * (length + width)",
                input_values={
                    "length": data.length,
                    "width": data.width,
                },
                result=perimeter,
                unit="m",
            ),
            CalculationStep(
                label="Concrete volume",
                formula="perimeter * foundation_width * foundation_depth",
                input_values={
                    "perimeter": perimeter,
                    "foundation_width": data.foundation_width,
                    "foundation_depth": data.foundation_depth,
                },
                result=concrete_volume,
                unit="m3",
            ),
            CalculationStep(
                label="Concrete volume with reserve",
                formula="concrete_volume * (1 + reserve_percent / 100)",
                input_values={
                    "concrete_volume": concrete_volume,
                    "reserve_percent": data.reserve_percent,
                },
                result=concrete_volume_with_reserve,
                unit="m3",
            ),
        ],
        materials=[
            MaterialItem(
                name="Concrete",
                quantity=concrete_volume_with_reserve,
                unit="m3",
                waste_percent=data.reserve_percent,
            ),
        ],
        assumptions=[
            CalculationAssumption(
                key="reserve_percent",
                description="Concrete reserve is based on input reserve_percent.",
                source="user_input",
            ),
        ],
        warnings=_build_strip_foundation_warnings(data, concrete_volume),
    )


def _build_strip_foundation_warnings(
    data: StripFoundationInput,
    concrete_volume: float,
) -> list[CalculationWarning]:
    warnings: list[CalculationWarning] = []

    if data.reserve_percent > 30:
        warnings.append(
            CalculationWarning(
                code="high_reserve_percent",
                message="Reserve percentage is above 30%, which may indicate a conservative estimate.",
                severity="info",
            )
        )

    if data.foundation_width > min(data.length, data.width) / 2:
        warnings.append(
            CalculationWarning(
                code="large_foundation_width",
                message="Foundation width is large relative to the room dimensions.",
                severity="warning",
            )
        )

    if data.foundation_depth > min(data.length, data.width) / 2:
        warnings.append(
            CalculationWarning(
                code="large_foundation_depth",
                message="Foundation depth is large relative to the room dimensions.",
                severity="warning",
            )
        )

    if concrete_volume == 0:
        warnings.append(
            CalculationWarning(
                code="zero_volume",
                message="Calculated concrete volume is zero; check input dimensions.",
                severity="error",
            )
        )

    return warnings