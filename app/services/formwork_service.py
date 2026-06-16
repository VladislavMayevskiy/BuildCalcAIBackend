import math

from app.schemas.formwork import FormworkFoundationInput
from app.schemas.calculation_result import (
    CalculationResult,
    CalculationStep,
    CalculationAssumption,
    CalculationWarning,
    MaterialItem,
)


def calculate_formwork_foundation_v2(data: FormworkFoundationInput) -> CalculationResult:
    formwork_area = round(data.perimeter_m * data.height_m * data.sides_count, 2)
    area_with_waste = round(formwork_area * (1 + data.waste_percent / 100), 2)
    waste_reserve = round(area_with_waste - formwork_area, 2)

    steps = [
        CalculationStep(
            label="Formwork contact area",
            formula="perimeter_m * height_m * sides_count",
            input_values={
                "perimeter_m": data.perimeter_m,
                "height_m": data.height_m,
                "sides_count": data.sides_count,
            },
            result=formwork_area,
            unit="m2",
        ),
        CalculationStep(
            label="Formwork area with waste",
            formula="formwork_area * (1 + waste_percent / 100)",
            input_values={
                "formwork_area": formwork_area,
                "waste_percent": data.waste_percent,
            },
            result=area_with_waste,
            unit="m2",
        ),
        CalculationStep(
            label="Waste reserve",
            formula="area_with_waste - formwork_area",
            input_values={
                "area_with_waste": area_with_waste,
                "formwork_area": formwork_area,
            },
            result=waste_reserve,
            unit="m2",
        ),
    ]

    materials = [
        MaterialItem(
            name="Formwork (boards/panels)",
            quantity=area_with_waste,
            unit="m2",
            waste_percent=data.waste_percent,
        ),
    ]

    if data.panel_area_m2 is not None:
        panel_count = math.ceil(area_with_waste / data.panel_area_m2)
        steps.append(
            CalculationStep(
                label="Panel/board count",
                formula="ceil(area_with_waste / panel_area_m2)",
                input_values={
                    "area_with_waste": area_with_waste,
                    "panel_area_m2": data.panel_area_m2,
                },
                result=float(panel_count),
                unit="pcs",
            )
        )
        materials.append(
            MaterialItem(
                name="Formwork panels",
                quantity=float(panel_count),
                unit="pcs",
                waste_percent=data.waste_percent,
            )
        )

    return CalculationResult(
        calculation_type="formwork_foundation",
        steps=steps,
        materials=materials,
        assumptions=_build_formwork_assumptions(data),
        warnings=_build_formwork_warnings(data, formwork_area),
    )


def _build_formwork_assumptions(
    data: FormworkFoundationInput,
) -> list[CalculationAssumption]:
    assumptions = [
        CalculationAssumption(
            key="sides_count",
            description="Formwork area counts both formed faces by default (sides_count=2).",
            source="default" if data.sides_count == 2 else "user_input",
        ),
        CalculationAssumption(
            key="waste_percent",
            description="Waste/reuse reserve is based on input waste_percent.",
            source="user_input",
        ),
    ]
    if data.panel_area_m2 is None:
        assumptions.append(
            CalculationAssumption(
                key="panel_area_m2",
                description="No panel area provided; only total formwork area is returned, not panel count.",
                source="default",
            )
        )
    return assumptions


def _build_formwork_warnings(
    data: FormworkFoundationInput,
    formwork_area: float,
) -> list[CalculationWarning]:
    warnings: list[CalculationWarning] = []

    if data.waste_percent > 30:
        warnings.append(
            CalculationWarning(
                code="high_waste_percent",
                message="Waste percentage is above 30%, which may indicate a conservative estimate.",
                severity="info",
            )
        )

    if data.sides_count != 2:
        warnings.append(
            CalculationWarning(
                code="non_standard_sides_count",
                message="sides_count is not 2; verify how many faces are actually formed.",
                severity="info",
            )
        )

    if data.height_m > 3:
        warnings.append(
            CalculationWarning(
                code="large_formwork_height",
                message="Formwork height is large (>3 m); verify the input and bracing requirements.",
                severity="warning",
            )
        )

    if formwork_area == 0:
        warnings.append(
            CalculationWarning(
                code="zero_area",
                message="Calculated formwork area is zero; check input dimensions.",
                severity="error",
            )
        )

    return warnings
