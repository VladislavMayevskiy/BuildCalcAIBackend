import math

from app.schemas.tiles import (
    TilesAdhesiveInput,
    TilesFloorInput,
    TilesGroutInput,
    TilesWallInput,
)
from app.schemas.calculation_result import (
    CalculationResult,
    CalculationStep,
    CalculationAssumption,
    CalculationWarning,
    MaterialItem,
)


def _tiling_result(
    calculation_type: str,
    net_area: float,
    tile_length_m: float,
    tile_width_m: float,
    waste: float,
    adhesive_rate,
    grout_rate,
    pack_area,
    extra_steps: list[CalculationStep],
    warnings: list[CalculationWarning],
) -> CalculationResult:
    tile_area_with_waste = round(net_area * (1 + waste / 100), 3)
    tile_area = tile_length_m * tile_width_m
    tile_count = float(math.ceil(tile_area_with_waste / tile_area))

    steps = list(extra_steps)
    steps.append(
        CalculationStep(
            label="Tile area with waste",
            formula="net_area * (1 + waste_percent / 100)",
            input_values={"net_area": net_area, "waste_percent": waste},
            result=tile_area_with_waste,
            unit="m2",
        )
    )
    steps.append(
        CalculationStep(
            label="Tile count",
            formula="ceil(tile_area_with_waste / (tile_length_m * tile_width_m))",
            input_values={"tile_area_with_waste": tile_area_with_waste, "tile_area": round(tile_area, 5)},
            result=tile_count,
            unit="pcs",
        )
    )

    materials = [
        MaterialItem(name="Tiles (area)", quantity=tile_area_with_waste, unit="m2", waste_percent=waste),
        MaterialItem(name="Tiles", quantity=tile_count, unit="pcs", waste_percent=waste),
    ]

    if pack_area is not None:
        pack_count = float(math.ceil(tile_area_with_waste / pack_area))
        steps.append(
            CalculationStep(
                label="Pack count",
                formula="ceil(tile_area_with_waste / pack_area_m2)",
                input_values={"tile_area_with_waste": tile_area_with_waste, "pack_area_m2": pack_area},
                result=pack_count,
                unit="packs",
            )
        )
        materials.append(MaterialItem(name="Tile packs", quantity=pack_count, unit="packs"))

    if adhesive_rate is not None:
        adhesive_kg = round(net_area * adhesive_rate, 2)
        steps.append(
            CalculationStep(
                label="Adhesive quantity",
                formula="net_area * adhesive_kg_per_m2",
                input_values={"net_area": net_area, "adhesive_kg_per_m2": adhesive_rate},
                result=adhesive_kg,
                unit="kg",
            )
        )
        materials.append(MaterialItem(name="Tile adhesive", quantity=adhesive_kg, unit="kg"))

    if grout_rate is not None:
        grout_kg = round(net_area * grout_rate, 2)
        steps.append(
            CalculationStep(
                label="Grout quantity",
                formula="net_area * grout_kg_per_m2",
                input_values={"net_area": net_area, "grout_kg_per_m2": grout_rate},
                result=grout_kg,
                unit="kg",
            )
        )
        materials.append(MaterialItem(name="Grout", quantity=grout_kg, unit="kg"))

    return CalculationResult(
        calculation_type=calculation_type,
        steps=steps,
        materials=materials,
        assumptions=[
            CalculationAssumption(
                key="waste_percent",
                description="Tile area includes a cutting/waste reserve; tile and pack counts are rounded up.",
                source="user_input",
            ),
            CalculationAssumption(
                key="grout_estimate",
                description="Grout/adhesive quantities are approximate and depend on tile size, joint width, and substrate.",
                source="user_input",
            ),
        ],
        warnings=warnings,
    )


def calculate_tiles_floor_v2(data: TilesFloorInput) -> CalculationResult:
    waste = data.waste_percent or 0
    net_area = round(data.area_m2, 3)
    extra = [
        CalculationStep(
            label="Tile area",
            formula="area_m2",
            input_values={"area_m2": data.area_m2},
            result=net_area,
            unit="m2",
        )
    ]
    return _tiling_result(
        "tiles_floor", net_area, data.tile_length_m, data.tile_width_m, waste,
        data.adhesive_kg_per_m2, data.grout_kg_per_m2, data.pack_area_m2, extra, [],
    )


def calculate_tiles_wall_v2(data: TilesWallInput) -> CalculationResult:
    waste = data.waste_percent or 0
    gross_area = round(data.gross_area_m2, 3)
    openings_area = round(data.openings_area_m2 or 0, 3)
    net_area = round(max(gross_area - openings_area, 0), 3)

    extra = [
        CalculationStep(
            label="Gross tiled area",
            formula="gross_area_m2",
            input_values={"gross_area_m2": gross_area},
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
            label="Net tiled area",
            formula="max(gross_area - openings_area, 0)",
            input_values={"gross_area": gross_area, "openings_area": openings_area},
            result=net_area,
            unit="m2",
        ),
    ]

    warnings: list[CalculationWarning] = []
    if net_area <= 0:
        warnings.append(
            CalculationWarning(
                code="zero_net_area",
                message="Net tiled area is zero or negative; openings exceed the wall area.",
                severity="error",
            )
        )

    return _tiling_result(
        "tiles_wall", net_area, data.tile_length_m, data.tile_width_m, waste,
        data.adhesive_kg_per_m2, data.grout_kg_per_m2, data.pack_area_m2, extra, warnings,
    )


def calculate_tiles_adhesive_v2(data: TilesAdhesiveInput) -> CalculationResult:
    waste = data.waste_percent or 0
    adhesive_kg = round(data.area_m2 * data.adhesive_kg_per_m2 * (1 + waste / 100), 2)
    bags = float(math.ceil(adhesive_kg / data.bag_weight_kg))

    return CalculationResult(
        calculation_type="tiles_adhesive",
        steps=[
            CalculationStep(
                label="Adhesive quantity",
                formula="area_m2 * adhesive_kg_per_m2 * (1 + waste_percent / 100)",
                input_values={"area_m2": data.area_m2, "adhesive_kg_per_m2": data.adhesive_kg_per_m2, "waste_percent": waste},
                result=adhesive_kg,
                unit="kg",
            ),
            CalculationStep(
                label="Bag count",
                formula="ceil(adhesive_kg / bag_weight_kg)",
                input_values={"adhesive_kg": adhesive_kg, "bag_weight_kg": data.bag_weight_kg},
                result=bags,
                unit="bags",
            ),
        ],
        materials=[
            MaterialItem(name="Tile adhesive", quantity=adhesive_kg, unit="kg", waste_percent=waste),
            MaterialItem(name="Tile adhesive bags", quantity=bags, unit="bags"),
        ],
        assumptions=[
            CalculationAssumption(
                key="adhesive_rate",
                description="Adhesive quantity uses the provided coverage rate plus a waste reserve.",
                source="user_input",
            ),
        ],
        warnings=[],
    )


def calculate_tiles_grout_v2(data: TilesGroutInput) -> CalculationResult:
    waste = data.waste_percent or 0
    grout_kg = round(data.area_m2 * data.grout_kg_per_m2 * (1 + waste / 100), 2)

    steps = [
        CalculationStep(
            label="Grout quantity",
            formula="area_m2 * grout_kg_per_m2 * (1 + waste_percent / 100)",
            input_values={"area_m2": data.area_m2, "grout_kg_per_m2": data.grout_kg_per_m2, "waste_percent": waste},
            result=grout_kg,
            unit="kg",
        ),
    ]
    materials = [
        MaterialItem(name="Grout", quantity=grout_kg, unit="kg", waste_percent=waste),
    ]

    if data.bag_weight_kg is not None:
        bags = float(math.ceil(grout_kg / data.bag_weight_kg))
        steps.append(
            CalculationStep(
                label="Bag count",
                formula="ceil(grout_kg / bag_weight_kg)",
                input_values={"grout_kg": grout_kg, "bag_weight_kg": data.bag_weight_kg},
                result=bags,
                unit="bags",
            )
        )
        materials.append(MaterialItem(name="Grout bags", quantity=bags, unit="bags"))

    return CalculationResult(
        calculation_type="tiles_grout",
        steps=steps,
        materials=materials,
        assumptions=[
            CalculationAssumption(
                key="grout_estimate",
                description="Grout quantity is approximate; actual use depends on tile size and joint width.",
                source="user_input",
            ),
        ],
        warnings=[
            CalculationWarning(
                code="approximate_grout",
                message="Grout quantity is an approximation based on a per-area rate.",
                severity="info",
            ),
        ],
    )
