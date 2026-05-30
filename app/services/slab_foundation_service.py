from app.schemas.slab_foundation import SlabFoundationInput
from app.schemas.calculation_result import (
    CalculationResult,
    CalculationStep,
    CalculationAssumption,
    CalculationWarning,
    MaterialItem,
)


def calculate_slab_foundation_v2(data: SlabFoundationInput) -> CalculationResult:
    slab_area = round(data.length * data.width, 2)
    concrete_volume = round(slab_area * data.slab_thickness, 2)
    concrete_volume_with_reserve = round(
        concrete_volume * (1 + data.reserve_percent / 100),
        2,
    )

    warnings = []
    if data.reserve_percent > 30:
        warnings.append(
            CalculationWarning(
                code="high_reserve_percent",
                message="Reserve percentage is above 30%, which may indicate a conservative estimate.",
                severity="info",
            )
        )
    if data.slab_thickness > min(data.length, data.width) / 5:
        warnings.append(
            CalculationWarning(
                code="thickness_too_large",
                message="Slab thickness is large relative to the slab footprint.",
                severity="warning",
            )
        )

    return CalculationResult(
        calculation_type="slab_foundation",
        steps=[
            CalculationStep(
                label="Slab area",
                formula="length * width",
                input_values={
                    "length": data.length,
                    "width": data.width,
                },
                result=slab_area,
                unit="m2",
            ),
            CalculationStep(
                label="Concrete volume",
                formula="slab_area * slab_thickness",
                input_values={
                    "slab_area": slab_area,
                    "slab_thickness": data.slab_thickness,
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
        warnings=warnings,
    )
