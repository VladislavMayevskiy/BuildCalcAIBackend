from app.schemas.calculation_result import (
    CalculationAssumption,
    CalculationResult,
    CalculationWarning,
)
from app.schemas.estimate import (
    AggregatedMaterialItem,
    EstimateResult,
    EstimateMaterialItem,
    MaterialAggregationResult,
)


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


def aggregate_materials(
    calculation_results: list[CalculationResult],
) -> MaterialAggregationResult:
    """Deterministically aggregate materials across multiple CalculationResults.

    Materials are grouped by (name, unit). Quantities are summed and the source
    calculation_types are preserved. No prices are invented: unit/total prices
    stay None and a warning is emitted because no stored price data is used.
    """
    grouped: dict[tuple[str, str], AggregatedMaterialItem] = {}
    order: list[tuple[str, str]] = []

    for result in calculation_results:
        source = result.calculation_type
        for material in result.materials:
            key = (material.name, material.unit)
            if key not in grouped:
                grouped[key] = AggregatedMaterialItem(
                    name=material.name,
                    unit=material.unit,
                    category=None,
                    total_quantity=0.0,
                    sources=[],
                    unit_price=None,
                    total_price=None,
                )
                order.append(key)
            item = grouped[key]
            item.total_quantity = round(item.total_quantity + material.quantity, 4)
            if source not in item.sources:
                item.sources.append(source)

    materials = [grouped[key] for key in order]

    warnings = [
        CalculationWarning(
            code="prices_missing",
            message="No stored price data was applied; quantities are aggregated without costs.",
            severity="info",
        )
    ]
    assumptions = [
        CalculationAssumption(
            key="grouping",
            description="Materials are grouped by name and unit; category grouping is planned.",
            source="aggregation_rule",
        ),
    ]

    return MaterialAggregationResult(
        materials=materials,
        subtotal_materials=None,
        currency="UAH",
        assumptions=assumptions,
        warnings=warnings,
    )