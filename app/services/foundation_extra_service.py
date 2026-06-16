import math

from app.schemas.foundation_extra import (
    CushionInput,
    FoundationInsulationInput,
    FoundationWaterproofingInput,
    PileInput,
)
from app.schemas.calculation_result import (
    CalculationResult,
    CalculationStep,
    CalculationAssumption,
    CalculationWarning,
    MaterialItem,
)


def calculate_pile_v2(data: PileInput) -> CalculationResult:
    reserve = data.reserve_percent or 0
    single_pile_volume = round(math.pi / 4 * data.pile_diameter_m ** 2 * data.pile_length_m, 4)
    total_pile_volume = round(single_pile_volume * data.pile_count, 4)
    volume_with_reserve = round(total_pile_volume * (1 + reserve / 100), 4)
    total_pile_length = round(data.pile_length_m * data.pile_count, 3)

    steps = [
        CalculationStep(
            label="Single pile volume",
            formula="pi/4 * pile_diameter_m^2 * pile_length_m",
            input_values={"pile_diameter_m": data.pile_diameter_m, "pile_length_m": data.pile_length_m},
            result=single_pile_volume,
            unit="m3",
        ),
        CalculationStep(
            label="Total pile concrete volume",
            formula="single_pile_volume * pile_count",
            input_values={"single_pile_volume": single_pile_volume, "pile_count": data.pile_count},
            result=total_pile_volume,
            unit="m3",
        ),
        CalculationStep(
            label="Concrete volume with reserve",
            formula="total_pile_volume * (1 + reserve_percent / 100)",
            input_values={"total_pile_volume": total_pile_volume, "reserve_percent": reserve},
            result=volume_with_reserve,
            unit="m3",
        ),
        CalculationStep(
            label="Total pile length",
            formula="pile_length_m * pile_count",
            input_values={"pile_length_m": data.pile_length_m, "pile_count": data.pile_count},
            result=total_pile_length,
            unit="m",
        ),
    ]

    materials = [
        MaterialItem(name="Concrete", quantity=volume_with_reserve, unit="m3", waste_percent=reserve),
    ]

    assumptions = [
        CalculationAssumption(
            key="circular_section",
            description="Each pile is treated as a circular cylinder.",
            source="standard_geometry",
        ),
        CalculationAssumption(
            key="reserve_percent",
            description="Concrete reserve is based on input reserve_percent.",
            source="user_input",
        ),
    ]

    if data.rebar_kg_per_m3 is not None:
        rebar_estimate = round(total_pile_volume * data.rebar_kg_per_m3, 2)
        steps.append(
            CalculationStep(
                label="Reinforcement estimate",
                formula="total_pile_volume * rebar_kg_per_m3",
                input_values={"total_pile_volume": total_pile_volume, "rebar_kg_per_m3": data.rebar_kg_per_m3},
                result=rebar_estimate,
                unit="kg",
            )
        )
        materials.append(MaterialItem(name="Rebar (estimate)", quantity=rebar_estimate, unit="kg"))
        assumptions.append(
            CalculationAssumption(
                key="rebar_rate",
                description="Reinforcement is a rough estimate from rebar_kg_per_m3, not a structural design.",
                source="user_input",
            )
        )

    warnings: list[CalculationWarning] = []
    if data.pile_diameter_m > 2:
        warnings.append(
            CalculationWarning(
                code="large_pile_diameter",
                message="Pile diameter above 2 m is unusual; verify the input.",
                severity="warning",
            )
        )
    if data.pile_length_m > 30:
        warnings.append(
            CalculationWarning(
                code="long_pile",
                message="Pile length above 30 m is unusual; verify the input.",
                severity="info",
            )
        )

    return CalculationResult(
        calculation_type="foundation_pile",
        steps=steps,
        materials=materials,
        assumptions=assumptions,
        warnings=warnings,
    )


def calculate_cushion_v2(data: CushionInput) -> CalculationResult:
    waste = data.waste_percent or 0
    sand_thickness = data.sand_thickness_m or 0
    gravel_thickness = data.gravel_thickness_m or 0

    area = round(data.length_m * data.width_m, 3)
    sand_volume = round(area * sand_thickness * (1 + waste / 100), 3)
    gravel_volume = round(area * gravel_thickness * (1 + waste / 100), 3)

    steps = [
        CalculationStep(
            label="Cushion footprint area",
            formula="length_m * width_m",
            input_values={"length_m": data.length_m, "width_m": data.width_m},
            result=area,
            unit="m2",
        ),
        CalculationStep(
            label="Sand cushion volume (with waste)",
            formula="area * sand_thickness_m * (1 + waste_percent / 100)",
            input_values={"area": area, "sand_thickness_m": sand_thickness, "waste_percent": waste},
            result=sand_volume,
            unit="m3",
        ),
        CalculationStep(
            label="Gravel cushion volume (with waste)",
            formula="area * gravel_thickness_m * (1 + waste_percent / 100)",
            input_values={"area": area, "gravel_thickness_m": gravel_thickness, "waste_percent": waste},
            result=gravel_volume,
            unit="m3",
        ),
    ]

    materials: list[MaterialItem] = []
    if sand_volume > 0:
        materials.append(MaterialItem(name="Sand", quantity=sand_volume, unit="m3", waste_percent=waste))
    if gravel_volume > 0:
        materials.append(MaterialItem(name="Gravel", quantity=gravel_volume, unit="m3", waste_percent=waste))

    assumptions = [
        CalculationAssumption(
            key="layer_thicknesses",
            description="Sand and gravel cushion volumes use the footprint area times each layer thickness.",
            source="user_input",
        ),
    ]

    if data.geotextile_overlap_percent is not None:
        geotextile_area = round(area * (1 + data.geotextile_overlap_percent / 100), 3)
        steps.append(
            CalculationStep(
                label="Geotextile area (with overlap)",
                formula="area * (1 + geotextile_overlap_percent / 100)",
                input_values={"area": area, "geotextile_overlap_percent": data.geotextile_overlap_percent},
                result=geotextile_area,
                unit="m2",
            )
        )
        materials.append(MaterialItem(name="Geotextile", quantity=geotextile_area, unit="m2"))
        assumptions.append(
            CalculationAssumption(
                key="geotextile_overlap",
                description="Geotextile area adds an overlap allowance over the footprint area.",
                source="user_input",
            )
        )

    return CalculationResult(
        calculation_type="foundation_cushion",
        steps=steps,
        materials=materials,
        assumptions=assumptions,
        warnings=[],
    )


def calculate_foundation_waterproofing_v2(
    data: FoundationWaterproofingInput,
) -> CalculationResult:
    overlap = data.overlap_percent or 0
    waste = data.waste_percent or 0
    base_area = round(data.base_area_m2(), 3)
    area_per_layer = round(base_area * (1 + overlap / 100), 3)
    total_membrane_area = round(area_per_layer * data.layers_count * (1 + waste / 100), 3)

    steps = [
        CalculationStep(
            label="Waterproofing surface area",
            formula="surface_area_m2 or 2*(length_m+width_m)*height_m",
            input_values={
                "surface_area_m2": data.surface_area_m2,
                "length_m": data.length_m,
                "width_m": data.width_m,
                "height_m": data.height_m,
            },
            result=base_area,
            unit="m2",
        ),
        CalculationStep(
            label="Area per layer (with overlap)",
            formula="base_area * (1 + overlap_percent / 100)",
            input_values={"base_area": base_area, "overlap_percent": overlap},
            result=area_per_layer,
            unit="m2",
        ),
        CalculationStep(
            label="Total membrane area (layers + waste)",
            formula="area_per_layer * layers_count * (1 + waste_percent / 100)",
            input_values={"area_per_layer": area_per_layer, "layers_count": data.layers_count, "waste_percent": waste},
            result=total_membrane_area,
            unit="m2",
        ),
    ]

    materials = [
        MaterialItem(name="Waterproofing membrane", quantity=total_membrane_area, unit="m2", waste_percent=waste),
    ]

    assumptions = [
        CalculationAssumption(
            key="surface_area_method",
            description="If dimensions are used, vertical wall area = perimeter * height.",
            source="standard_geometry",
        ),
    ]

    if data.primer_coverage_m2_per_l is not None:
        primer_liters = round(base_area / data.primer_coverage_m2_per_l, 3)
        steps.append(
            CalculationStep(
                label="Primer quantity",
                formula="base_area / primer_coverage_m2_per_l",
                input_values={"base_area": base_area, "primer_coverage_m2_per_l": data.primer_coverage_m2_per_l},
                result=primer_liters,
                unit="l",
            )
        )
        materials.append(MaterialItem(name="Primer", quantity=primer_liters, unit="l"))

    warnings: list[CalculationWarning] = []
    if data.layers_count > 3:
        warnings.append(
            CalculationWarning(
                code="many_layers",
                message="More than 3 waterproofing layers is unusual; verify the spec.",
                severity="info",
            )
        )

    return CalculationResult(
        calculation_type="foundation_waterproofing",
        steps=steps,
        materials=materials,
        assumptions=assumptions,
        warnings=warnings,
    )


def calculate_foundation_insulation_v2(
    data: FoundationInsulationInput,
) -> CalculationResult:
    waste = data.waste_percent or 0
    area_with_waste = round(data.area_m2 * (1 + waste / 100), 3)
    volume = round(data.area_m2 * data.insulation_thickness_mm / 1000, 4)

    steps = [
        CalculationStep(
            label="Insulation area with waste",
            formula="area_m2 * (1 + waste_percent / 100)",
            input_values={"area_m2": data.area_m2, "waste_percent": waste},
            result=area_with_waste,
            unit="m2",
        ),
        CalculationStep(
            label="Insulation volume",
            formula="area_m2 * insulation_thickness_mm / 1000",
            input_values={"area_m2": data.area_m2, "insulation_thickness_mm": data.insulation_thickness_mm},
            result=volume,
            unit="m3",
        ),
    ]

    materials = [
        MaterialItem(name="Insulation boards", quantity=area_with_waste, unit="m2", waste_percent=waste),
    ]
    assumptions = [
        CalculationAssumption(
            key="waste_percent",
            description="Insulation area includes a cutting/waste reserve.",
            source="user_input",
        ),
    ]

    if data.board_length_m is not None and data.board_width_m is not None:
        board_area = data.board_length_m * data.board_width_m
        board_count = float(math.ceil(area_with_waste / board_area))
        steps.append(
            CalculationStep(
                label="Insulation board count",
                formula="ceil(area_with_waste / (board_length_m * board_width_m))",
                input_values={"area_with_waste": area_with_waste, "board_area": round(board_area, 4)},
                result=board_count,
                unit="pcs",
            )
        )
        materials.append(MaterialItem(name="Insulation board pieces", quantity=board_count, unit="pcs"))

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

    return CalculationResult(
        calculation_type="foundation_insulation",
        steps=steps,
        materials=materials,
        assumptions=assumptions,
        warnings=[],
    )
