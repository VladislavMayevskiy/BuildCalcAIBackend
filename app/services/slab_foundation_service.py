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
    if data.slab_thickness < 0.1:
        warnings.append(
            CalculationWarning(
                code="thin_slab_thickness",
                message="Slab thickness is below 0.1 m, which is unusually thin for a foundation slab.",
                severity="info",
            )
        )
    if data.reserve_percent == 0:
        warnings.append(
            CalculationWarning(
                code="no_reserve",
                message="Reserve percentage is 0%; no allowance for spillage or over-excavation.",
                severity="info",
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
            CalculationAssumption(
                key="slab_area_method",
                description="Slab area uses plan dimensions: length * width.",
                source="standard_geometry",
            ),
            CalculationAssumption(
                key="concrete_only",
                description="Only concrete volume is computed; rebar mesh and formwork are separate calculators.",
                source="scope",
            ),
        ],
        warnings=warnings,
    )
