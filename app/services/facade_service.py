import math

from app.schemas.facade import (
    FacadeAreaInput,
    FacadeInsulationInput,
    FacadePaintInput,
    FacadePlasterInput,
)
from app.schemas.calculation_result import (
    CalculationResult,
    CalculationStep,
    CalculationAssumption,
    CalculationWarning,
    MaterialItem,
)


def calculate_facade_area_v2(data: FacadeAreaInput) -> CalculationResult:
    waste = data.waste_percent or 0
    gross_area = round(data.gross_area_m2(), 3)
    openings_area = round(data.openings_area_m2 or 0, 3)
    net_area = round(max(gross_area - openings_area, 0), 3)
    area_with_waste = round(net_area * (1 + waste / 100), 3)
    reserve = round(area_with_waste - net_area, 3)

    warnings: list[CalculationWarning] = []
    if net_area <= 0:
        warnings.append(
            CalculationWarning(
                code="zero_net_area",
                message="Net facade area is zero or negative; openings exceed the facade area.",
                severity="error",
            )
        )

    return CalculationResult(
        calculation_type="facade_area",
        steps=[
            CalculationStep(
                label="Gross facade area",
                formula="sum(width_m * height_m)",
                input_values={"panel_count": len(data.facades)},
                result=gross_area,
                unit="m2",
            ),
            CalculationStep(
                label="Openings area",
                formula="openings_area_m2",
                input_values={"openings_area_m2": openings_area},
                result=openings_area,
                unit="m2",
            ),
            CalculationStep(
                label="Net facade area",
                formula="max(gross_area - openings_area, 0)",
                input_values={"gross_area": gross_area, "openings_area": openings_area},
                result=net_area,
                unit="m2",
            ),
            CalculationStep(
                label="Area with waste/reserve",
                formula="net_area * (1 + waste_percent / 100)",
                input_values={"net_area": net_area, "waste_percent": waste},
                result=area_with_waste,
                unit="m2",
            ),
            CalculationStep(
                label="Waste/reserve area",
                formula="area_with_waste - net_area",
                input_values={"area_with_waste": area_with_waste, "net_area": net_area},
                result=reserve,
                unit="m2",
            ),
        ],
        materials=[
            MaterialItem(name="Facade area", quantity=area_with_waste, unit="m2", waste_percent=waste),
        ],
        assumptions=[
            CalculationAssumption(
                key="waste_percent",
                description="Net facade area includes a waste/reserve allowance.",
                source="user_input",
            ),
        ],
        warnings=warnings,
    )


def calculate_facade_insulation_v2(data: FacadeInsulationInput) -> CalculationResult:
    waste = data.waste_percent or 0
    area_with_waste = round(data.area_m2 * (1 + waste / 100), 3)
    board_area = data.board_length_m * data.board_width_m
    board_count = float(math.ceil(area_with_waste / board_area))

    steps = [
        CalculationStep(
            label="Insulation area with waste",
            formula="area_m2 * (1 + waste_percent / 100)",
            input_values={"area_m2": data.area_m2, "waste_percent": waste},
            result=area_with_waste,
            unit="m2",
        ),
        CalculationStep(
            label="Board count",
            formula="ceil(area_with_waste / (board_length_m * board_width_m))",
            input_values={"area_with_waste": area_with_waste, "board_area": round(board_area, 4)},
            result=board_count,
            unit="pcs",
        ),
    ]

    materials = [
        MaterialItem(name="Insulation boards", quantity=board_count, unit="pcs", waste_percent=waste),
        MaterialItem(name="Insulation area", quantity=area_with_waste, unit="m2", waste_percent=waste),
    ]

    if data.adhesive_coverage_m2_per_bag is not None:
        adhesive_bags = float(math.ceil(area_with_waste / data.adhesive_coverage_m2_per_bag))
        steps.append(
            CalculationStep(
                label="Adhesive bags",
                formula="ceil(area_with_waste / adhesive_coverage_m2_per_bag)",
                input_values={"area_with_waste": area_with_waste, "adhesive_coverage_m2_per_bag": data.adhesive_coverage_m2_per_bag},
                result=adhesive_bags,
                unit="bags",
            )
        )
        materials.append(MaterialItem(name="Adhesive", quantity=adhesive_bags, unit="bags"))

    if data.dowels_per_m2 is not None:
        dowel_count = float(math.ceil(area_with_waste * data.dowels_per_m2))
        steps.append(
            CalculationStep(
                label="Dowel count",
                formula="ceil(area_with_waste * dowels_per_m2)",
                input_values={"area_with_waste": area_with_waste, "dowels_per_m2": data.dowels_per_m2},
                result=dowel_count,
                unit="pcs",
            )
        )
        materials.append(MaterialItem(name="Dowels", quantity=dowel_count, unit="pcs"))

    mesh_overlap = data.mesh_overlap_percent or 0
    mesh_area = round(area_with_waste * (1 + mesh_overlap / 100), 3)
    steps.append(
        CalculationStep(
            label="Mesh area",
            formula="area_with_waste * (1 + mesh_overlap_percent / 100)",
            input_values={"area_with_waste": area_with_waste, "mesh_overlap_percent": mesh_overlap},
            result=mesh_area,
            unit="m2",
        )
    )
    materials.append(MaterialItem(name="Reinforcing mesh", quantity=mesh_area, unit="m2"))

    return CalculationResult(
        calculation_type="facade_insulation",
        steps=steps,
        materials=materials,
        assumptions=[
            CalculationAssumption(
                key="waste_percent",
                description="Insulation area includes a cutting/waste reserve; counts are rounded up.",
                source="user_input",
            ),
        ],
        warnings=[],
    )


def calculate_facade_plaster_v2(data: FacadePlasterInput) -> CalculationResult:
    waste = data.waste_percent or 0
    area_with_waste = round(data.area_m2 * (1 + waste / 100), 3)
    plaster_kg = round(area_with_waste * data.plaster_kg_per_m2, 2)

    steps = [
        CalculationStep(
            label="Plaster area with waste",
            formula="area_m2 * (1 + waste_percent / 100)",
            input_values={"area_m2": data.area_m2, "waste_percent": waste},
            result=area_with_waste,
            unit="m2",
        ),
        CalculationStep(
            label="Plaster quantity",
            formula="area_with_waste * plaster_kg_per_m2",
            input_values={"area_with_waste": area_with_waste, "plaster_kg_per_m2": data.plaster_kg_per_m2},
            result=plaster_kg,
            unit="kg",
        ),
    ]
    materials = [
        MaterialItem(name="Plaster", quantity=plaster_kg, unit="kg", waste_percent=waste),
    ]

    if data.primer_coverage_m2_per_l is not None:
        primer_liters = round(data.area_m2 / data.primer_coverage_m2_per_l, 3)
        steps.append(
            CalculationStep(
                label="Primer quantity",
                formula="area_m2 / primer_coverage_m2_per_l",
                input_values={"area_m2": data.area_m2, "primer_coverage_m2_per_l": data.primer_coverage_m2_per_l},
                result=primer_liters,
                unit="l",
            )
        )
        materials.append(MaterialItem(name="Primer", quantity=primer_liters, unit="l"))

    return CalculationResult(
        calculation_type="facade_plaster",
        steps=steps,
        materials=materials,
        assumptions=[
            CalculationAssumption(
                key="plaster_rate",
                description="Plaster quantity uses the provided plaster_kg_per_m2 rate.",
                source="user_input",
            ),
        ],
        warnings=[],
    )


def calculate_facade_paint_v2(data: FacadePaintInput) -> CalculationResult:
    waste = data.waste_percent or 0
    area_with_waste = round(data.area_m2 * (1 + waste / 100), 3)
    paint_liters = round(area_with_waste * data.coats_count / data.paint_coverage_m2_per_l, 3)

    steps = [
        CalculationStep(
            label="Paint area with waste",
            formula="area_m2 * (1 + waste_percent / 100)",
            input_values={"area_m2": data.area_m2, "waste_percent": waste},
            result=area_with_waste,
            unit="m2",
        ),
        CalculationStep(
            label="Paint quantity",
            formula="area_with_waste * coats_count / paint_coverage_m2_per_l",
            input_values={
                "area_with_waste": area_with_waste,
                "coats_count": data.coats_count,
                "paint_coverage_m2_per_l": data.paint_coverage_m2_per_l,
            },
            result=paint_liters,
            unit="l",
        ),
    ]
    materials = [
        MaterialItem(name="Paint", quantity=paint_liters, unit="l", waste_percent=waste),
    ]

    if data.primer_coverage_m2_per_l is not None:
        primer_liters = round(data.area_m2 / data.primer_coverage_m2_per_l, 3)
        steps.append(
            CalculationStep(
                label="Primer quantity",
                formula="area_m2 / primer_coverage_m2_per_l",
                input_values={"area_m2": data.area_m2, "primer_coverage_m2_per_l": data.primer_coverage_m2_per_l},
                result=primer_liters,
                unit="l",
            )
        )
        materials.append(MaterialItem(name="Primer", quantity=primer_liters, unit="l"))

    return CalculationResult(
        calculation_type="facade_paint",
        steps=steps,
        materials=materials,
        assumptions=[
            CalculationAssumption(
                key="coats_count",
                description="Paint quantity multiplies area by the number of coats and divides by coverage.",
                source="user_input",
            ),
        ],
        warnings=[],
    )
