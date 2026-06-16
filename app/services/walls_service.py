import math

from app.schemas.walls import WallBlocksInput, WallBricksInput, WallMortarInput
from app.schemas.calculation_result import (
    CalculationResult,
    CalculationStep,
    CalculationAssumption,
    CalculationWarning,
    MaterialItem,
)


def _net_area_steps(gross_area: float, openings_area: float) -> tuple[float, list[CalculationStep]]:
    net_area = round(max(gross_area - openings_area, 0), 3)
    steps = [
        CalculationStep(
            label="Gross wall area",
            formula="wall_length_m * wall_height_m",
            input_values={},
            result=round(gross_area, 3),
            unit="m2",
        ),
        CalculationStep(
            label="Openings area",
            formula="openings_area_m2",
            input_values={"openings_area_m2": round(openings_area, 3)},
            result=round(openings_area, 3),
            unit="m2",
        ),
        CalculationStep(
            label="Net wall area",
            formula="max(gross_area - openings_area, 0)",
            input_values={"gross_area": round(gross_area, 3), "openings_area": round(openings_area, 3)},
            result=net_area,
            unit="m2",
        ),
    ]
    return net_area, steps


def _net_area_warning(net_area: float) -> list[CalculationWarning]:
    if net_area <= 0:
        return [
            CalculationWarning(
                code="zero_net_area",
                message="Net wall area is zero or negative; openings exceed the wall area.",
                severity="error",
            )
        ]
    return []


def calculate_wall_blocks_v2(data: WallBlocksInput) -> CalculationResult:
    waste = data.waste_percent or 0
    joint = data.joint_thickness_m or 0
    gross_area = data.wall_length_m * data.wall_height_m
    openings_area = data.openings_area_m2 or 0
    net_area, steps = _net_area_steps(gross_area, openings_area)

    block_face = (data.block_length_m + joint) * (data.block_height_m + joint)
    blocks_per_m2 = 1 / block_face
    block_count = net_area * blocks_per_m2
    block_count_with_waste = float(math.ceil(block_count * (1 + waste / 100)))

    steps.append(
        CalculationStep(
            label="Block count",
            formula="net_area / ((block_length_m + joint) * (block_height_m + joint))",
            input_values={"net_area": net_area, "block_face_m2": round(block_face, 5)},
            result=round(block_count, 2),
            unit="pcs",
        )
    )
    steps.append(
        CalculationStep(
            label="Block count with waste",
            formula="ceil(block_count * (1 + waste_percent / 100))",
            input_values={"block_count": round(block_count, 2), "waste_percent": waste},
            result=block_count_with_waste,
            unit="pcs",
        )
    )

    materials = [
        MaterialItem(name="Blocks", quantity=block_count_with_waste, unit="pcs", waste_percent=waste),
    ]

    if data.mortar_kg_per_m2 is not None:
        mortar_kg = round(net_area * data.mortar_kg_per_m2, 2)
        steps.append(
            CalculationStep(
                label="Mortar/glue quantity",
                formula="net_area * mortar_kg_per_m2",
                input_values={"net_area": net_area, "mortar_kg_per_m2": data.mortar_kg_per_m2},
                result=mortar_kg,
                unit="kg",
            )
        )
        materials.append(MaterialItem(name="Block glue/mortar", quantity=mortar_kg, unit="kg"))

    return CalculationResult(
        calculation_type="walls_blocks",
        steps=steps,
        materials=materials,
        assumptions=[
            CalculationAssumption(
                key="joint_thickness",
                description="Block face area includes mortar joint thickness on length and height.",
                source="user_input",
            ),
        ],
        warnings=_net_area_warning(net_area),
    )


def calculate_wall_bricks_v2(data: WallBricksInput) -> CalculationResult:
    waste = data.waste_percent or 0
    joint = data.joint_thickness_m or 0
    layers = data.wall_thickness_bricks or 1
    gross_area = data.wall_length_m * data.wall_height_m
    openings_area = data.openings_area_m2 or 0
    net_area, steps = _net_area_steps(gross_area, openings_area)

    brick_face = (data.brick_length_m + joint) * (data.brick_height_m + joint)
    bricks_per_m2 = layers / brick_face
    brick_count = net_area * bricks_per_m2
    brick_count_with_waste = float(math.ceil(brick_count * (1 + waste / 100)))

    steps.append(
        CalculationStep(
            label="Brick count",
            formula="net_area * wall_thickness_bricks / ((brick_length_m + joint) * (brick_height_m + joint))",
            input_values={
                "net_area": net_area,
                "wall_thickness_bricks": layers,
                "brick_face_m2": round(brick_face, 5),
            },
            result=round(brick_count, 2),
            unit="pcs",
        )
    )
    steps.append(
        CalculationStep(
            label="Brick count with waste",
            formula="ceil(brick_count * (1 + waste_percent / 100))",
            input_values={"brick_count": round(brick_count, 2), "waste_percent": waste},
            result=brick_count_with_waste,
            unit="pcs",
        )
    )

    materials = [
        MaterialItem(name="Bricks", quantity=brick_count_with_waste, unit="pcs", waste_percent=waste),
    ]
    assumptions = [
        CalculationAssumption(
            key="joint_thickness",
            description="Brick face area includes mortar joint thickness on length and height.",
            source="user_input",
        ),
        CalculationAssumption(
            key="wall_thickness_bricks",
            description="Brick count is multiplied by wall_thickness_bricks (number of brick leaves).",
            source="user_input",
        ),
    ]

    warnings = _net_area_warning(net_area)

    if data.brick_width_m is not None:
        wall_thickness_m = data.brick_width_m * layers
        masonry_volume = net_area * wall_thickness_m
        brick_volume_total = brick_count * (data.brick_length_m * data.brick_height_m * data.brick_width_m)
        mortar_volume = round(max(masonry_volume - brick_volume_total, 0), 3)
        steps.append(
            CalculationStep(
                label="Mortar volume estimate",
                formula="net_area * wall_thickness_m - brick_count * brick_volume",
                input_values={
                    "masonry_volume": round(masonry_volume, 3),
                    "brick_volume_total": round(brick_volume_total, 3),
                },
                result=mortar_volume,
                unit="m3",
            )
        )
        materials.append(MaterialItem(name="Mortar", quantity=mortar_volume, unit="m3"))
        assumptions.append(
            CalculationAssumption(
                key="mortar_volume_method",
                description="Mortar volume = masonry volume minus solid brick volume (approximate).",
                source="standard_geometry",
            )
        )

    return CalculationResult(
        calculation_type="walls_bricks",
        steps=steps,
        materials=materials,
        assumptions=assumptions,
        warnings=warnings,
    )


def calculate_wall_mortar_v2(data: WallMortarInput) -> CalculationResult:
    waste = data.waste_percent or 0
    dry_mix_rate = data.dry_mix_kg_per_m3 or 1600

    if data.mortar_rate_m3_per_m2 is not None:
        mortar_volume = data.masonry_area_m2 * data.mortar_rate_m3_per_m2
        volume_formula = "masonry_area_m2 * mortar_rate_m3_per_m2"
        volume_inputs = {"masonry_area_m2": data.masonry_area_m2, "mortar_rate_m3_per_m2": data.mortar_rate_m3_per_m2}
    else:
        joint_fraction = data.joint_fraction or 0.2
        mortar_volume = data.masonry_area_m2 * data.wall_thickness_m * joint_fraction
        volume_formula = "masonry_area_m2 * wall_thickness_m * joint_fraction"
        volume_inputs = {
            "masonry_area_m2": data.masonry_area_m2,
            "wall_thickness_m": data.wall_thickness_m,
            "joint_fraction": joint_fraction,
        }

    mortar_volume = round(mortar_volume, 4)
    mortar_volume_with_waste = round(mortar_volume * (1 + waste / 100), 4)
    dry_mix_kg = round(mortar_volume_with_waste * dry_mix_rate, 2)

    steps = [
        CalculationStep(
            label="Mortar volume",
            formula=volume_formula,
            input_values=volume_inputs,
            result=mortar_volume,
            unit="m3",
        ),
        CalculationStep(
            label="Mortar volume with waste",
            formula="mortar_volume * (1 + waste_percent / 100)",
            input_values={"mortar_volume": mortar_volume, "waste_percent": waste},
            result=mortar_volume_with_waste,
            unit="m3",
        ),
        CalculationStep(
            label="Dry mix mass",
            formula="mortar_volume_with_waste * dry_mix_kg_per_m3",
            input_values={"mortar_volume_with_waste": mortar_volume_with_waste, "dry_mix_kg_per_m3": dry_mix_rate},
            result=dry_mix_kg,
            unit="kg",
        ),
    ]

    materials = [
        MaterialItem(name="Mortar", quantity=mortar_volume_with_waste, unit="m3", waste_percent=waste),
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
        calculation_type="walls_mortar",
        steps=steps,
        materials=materials,
        assumptions=[
            CalculationAssumption(
                key="mortar_estimate",
                description="Mortar quantity is approximate; either a direct rate or a joint fraction of masonry volume is used.",
                source="user_input" if data.mortar_rate_m3_per_m2 is not None else "default",
            ),
        ],
        warnings=[
            CalculationWarning(
                code="approximate_mortar",
                message="Mortar quantity is an approximation; actual usage depends on workmanship, unit type, and joint profile.",
                severity="info",
            ),
        ],
    )
