import math

from app.schemas.floors import FloorInsulationInput, FloorLaminateInput, FloorScreedInput
from app.schemas.calculation_result import (
    CalculationResult,
    CalculationStep,
    CalculationAssumption,
    CalculationWarning,
    MaterialItem,
)


def calculate_floor_screed_v2(data: FloorScreedInput) -> CalculationResult:
    waste = data.waste_percent or 0
    density = data.density_kg_per_m3 or 1800

    volume = round(data.area_m2 * data.thickness_m, 4)
    volume_with_waste = round(volume * (1 + waste / 100), 4)
    dry_mix_kg = round(volume_with_waste * density, 2)

    steps = [
        CalculationStep(
            label="Screed volume",
            formula="area_m2 * thickness_m",
            input_values={"area_m2": data.area_m2, "thickness_m": data.thickness_m},
            result=volume,
            unit="m3",
        ),
        CalculationStep(
            label="Screed volume with waste",
            formula="volume * (1 + waste_percent / 100)",
            input_values={"volume": volume, "waste_percent": waste},
            result=volume_with_waste,
            unit="m3",
        ),
        CalculationStep(
            label="Dry mix mass",
            formula="volume_with_waste * density_kg_per_m3",
            input_values={"volume_with_waste": volume_with_waste, "density_kg_per_m3": density},
            result=dry_mix_kg,
            unit="kg",
        ),
    ]

    materials = [
        MaterialItem(name="Screed", quantity=volume_with_waste, unit="m3", waste_percent=waste),
        MaterialItem(name="Dry mix", quantity=dry_mix_kg, unit="kg"),
    ]

    if data.bag_weight_kg is not None:
        bags = float(math.ceil(dry_mix_kg / data.bag_weight_kg))
        steps.append(
            CalculationStep(
                label="Bag count",
                formula="ceil(dry_mix_kg / bag_weight_kg)",
                input_values={"dry_mix_kg": dry_mix_kg, "bag_weight_kg": data.bag_weight_kg},
                result=bags,
                unit="bags",
            )
        )
        materials.append(MaterialItem(name="Dry mix bags", quantity=bags, unit="bags"))

    return CalculationResult(
        calculation_type="floors_screed",
        steps=steps,
        materials=materials,
        assumptions=[
            CalculationAssumption(
                key="dry_mix_density",
                description="Dry mix mass uses density default 1800 kg/m3 unless provided.",
                source="default" if data.density_kg_per_m3 is None else "user_input",
            ),
        ],
        warnings=[],
    )


def calculate_floor_insulation_v2(data: FloorInsulationInput) -> CalculationResult:
    waste = data.waste_percent or 0
    area_with_waste = round(data.area_m2 * (1 + waste / 100), 3)
    volume = round(data.area_m2 * data.thickness_mm / 1000, 4)

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
            formula="area_m2 * thickness_mm / 1000",
            input_values={"area_m2": data.area_m2, "thickness_mm": data.thickness_mm},
            result=volume,
            unit="m3",
        ),
    ]
    materials = [
        MaterialItem(name="Floor insulation", quantity=area_with_waste, unit="m2", waste_percent=waste),
    ]

    if data.board_length_m is not None and data.board_width_m is not None:
        board_area = data.board_length_m * data.board_width_m
        board_count = float(math.ceil(area_with_waste / board_area))
        steps.append(
            CalculationStep(
                label="Board count",
                formula="ceil(area_with_waste / (board_length_m * board_width_m))",
                input_values={"area_with_waste": area_with_waste, "board_area": round(board_area, 4)},
                result=board_count,
                unit="pcs",
            )
        )
        materials.append(MaterialItem(name="Insulation board pieces", quantity=board_count, unit="pcs"))

    return CalculationResult(
        calculation_type="floors_insulation",
        steps=steps,
        materials=materials,
        assumptions=[
            CalculationAssumption(
                key="waste_percent",
                description="Insulation area includes a cutting/waste reserve.",
                source="user_input",
            ),
        ],
        warnings=[],
    )


def calculate_floor_laminate_v2(data: FloorLaminateInput) -> CalculationResult:
    waste = data.waste_percent or 0
    net_area = round(data.area_m2, 3)
    laminate_area = round(net_area * (1 + waste / 100), 3)

    steps = [
        CalculationStep(
            label="Net floor area",
            formula="area_m2",
            input_values={"area_m2": data.area_m2},
            result=net_area,
            unit="m2",
        ),
        CalculationStep(
            label="Laminate area with waste",
            formula="net_area * (1 + waste_percent / 100)",
            input_values={"net_area": net_area, "waste_percent": waste},
            result=laminate_area,
            unit="m2",
        ),
    ]
    materials = [
        MaterialItem(name="Laminate", quantity=laminate_area, unit="m2", waste_percent=waste),
    ]

    if data.pack_area_m2 is not None:
        pack_count = float(math.ceil(laminate_area / data.pack_area_m2))
        steps.append(
            CalculationStep(
                label="Pack count",
                formula="ceil(laminate_area / pack_area_m2)",
                input_values={"laminate_area": laminate_area, "pack_area_m2": data.pack_area_m2},
                result=pack_count,
                unit="packs",
            )
        )
        materials.append(MaterialItem(name="Laminate packs", quantity=pack_count, unit="packs"))

    if data.underlay_enabled:
        steps.append(
            CalculationStep(
                label="Underlay area",
                formula="net_area",
                input_values={"net_area": net_area},
                result=net_area,
                unit="m2",
            )
        )
        materials.append(MaterialItem(name="Underlay", quantity=net_area, unit="m2"))

    if data.perimeter_m is not None:
        baseboard_length = round(max(data.perimeter_m - (data.openings_width_m or 0), 0), 3)
        steps.append(
            CalculationStep(
                label="Baseboard length",
                formula="max(perimeter_m - openings_width_m, 0)",
                input_values={"perimeter_m": data.perimeter_m, "openings_width_m": data.openings_width_m or 0},
                result=baseboard_length,
                unit="m",
            )
        )
        materials.append(MaterialItem(name="Baseboard", quantity=baseboard_length, unit="m"))

    return CalculationResult(
        calculation_type="floors_laminate",
        steps=steps,
        materials=materials,
        assumptions=[
            CalculationAssumption(
                key="waste_percent",
                description="Laminate area includes a cutting/waste reserve (default 10%).",
                source="user_input",
            ),
        ],
        warnings=[],
    )
