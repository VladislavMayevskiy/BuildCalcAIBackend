from app.schemas.calculation_result import CalculationResult
from app.schemas.estimate import EstimateResult, EstimateMaterialItem


def generate_estimate_from_calculation(
    calculation_result: CalculationResult
) -> EstimateResult:
    materials_list: list[EstimateMaterialItem] = []

    for material in calculation_result.materials:
        estimate_material = EstimateMaterialItem(
            name=material.name,
            quantity=material.quantity,
            unit=material.unit,
            waste_percent=material.waste_percent,
            unit_price=None,
            total_price=None,
        )

        materials_list.append(estimate_material)

    estimate = EstimateResult(
        materials=materials_list,
        subtotal_materials=0,
        currency="UAH",
        assumptions=calculation_result.assumptions,
        warnings=calculation_result.warnings,
    )

    return estimate