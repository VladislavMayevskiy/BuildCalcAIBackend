import math

from app.schemas.earthworks import BackfillInput, ExcavationInput, TrenchInput
from app.schemas.calculation_result import (
    CalculationResult,
    CalculationStep,
    CalculationAssumption,
    CalculationWarning,
    MaterialItem,
)


def calculate_excavation_v2(data: ExcavationInput) -> CalculationResult:
    slope = data.slope_allowance_percent or 0
    bulking = data.bulking_percent or 0
    backfill = data.backfill_percent or 0
    waste = data.waste_percent or 0

    excavation_volume = round(data.length_m * data.width_m * data.depth_m, 3)
    volume_with_slope = round(excavation_volume * (1 + slope / 100), 3)
    volume_with_bulking = round(volume_with_slope * (1 + bulking / 100), 3)
    soil_removal_volume = round(volume_with_bulking * (1 + waste / 100), 3)
    backfill_volume = round(volume_with_slope * backfill / 100, 3)

    materials = [
        MaterialItem(name="Excavation work", quantity=volume_with_slope, unit="m3"),
        MaterialItem(
            name="Soil removal (loose)",
            quantity=soil_removal_volume,
            unit="m3",
            waste_percent=waste,
        ),
    ]
    if backfill_volume > 0:
        materials.append(
            MaterialItem(name="Backfill (compacted)", quantity=backfill_volume, unit="m3")
        )

    warnings: list[CalculationWarning] = []
    if data.depth_m > 4:
        warnings.append(
            CalculationWarning(
                code="deep_excavation",
                message="Excavation depth above 4 m usually requires shoring/sloping design.",
                severity="warning",
            )
        )
    if bulking > 50:
        warnings.append(
            CalculationWarning(
                code="high_bulking_percent",
                message="Bulking percent above 50% is unusually high; verify soil type.",
                severity="info",
            )
        )
    if excavation_volume == 0:
        warnings.append(
            CalculationWarning(
                code="zero_volume",
                message="Calculated excavation volume is zero; check dimensions.",
                severity="error",
            )
        )

    return CalculationResult(
        calculation_type="earthworks_excavation",
        steps=[
            CalculationStep(
                label="Excavation volume (in-situ)",
                formula="length_m * width_m * depth_m",
                input_values={"length_m": data.length_m, "width_m": data.width_m, "depth_m": data.depth_m},
                result=excavation_volume,
                unit="m3",
            ),
            CalculationStep(
                label="Volume with slope allowance",
                formula="excavation_volume * (1 + slope_allowance_percent / 100)",
                input_values={"excavation_volume": excavation_volume, "slope_allowance_percent": slope},
                result=volume_with_slope,
                unit="m3",
            ),
            CalculationStep(
                label="Volume with bulking factor",
                formula="volume_with_slope * (1 + bulking_percent / 100)",
                input_values={"volume_with_slope": volume_with_slope, "bulking_percent": bulking},
                result=volume_with_bulking,
                unit="m3",
            ),
            CalculationStep(
                label="Soil removal volume (loose, with waste)",
                formula="volume_with_bulking * (1 + waste_percent / 100)",
                input_values={"volume_with_bulking": volume_with_bulking, "waste_percent": waste},
                result=soil_removal_volume,
                unit="m3",
            ),
            CalculationStep(
                label="Backfill volume",
                formula="volume_with_slope * backfill_percent / 100",
                input_values={"volume_with_slope": volume_with_slope, "backfill_percent": backfill},
                result=backfill_volume,
                unit="m3",
            ),
        ],
        materials=materials,
        assumptions=[
            CalculationAssumption(
                key="bulking_factor",
                description="Bulking accounts for soil expansion when excavated (loose vs in-situ volume).",
                source="user_input",
            ),
            CalculationAssumption(
                key="slope_allowance",
                description="Slope allowance approximates extra excavation for battered/sloped sides.",
                source="user_input",
            ),
        ],
        warnings=warnings,
    )


def calculate_trench_v2(data: TrenchInput) -> CalculationResult:
    bedding_thickness = data.bedding_thickness_m or 0
    pipe_zone_height = data.pipe_zone_height_m or 0
    bulking = data.bulking_percent or 0

    cross_section = data.trench_width_m
    trench_volume = round(data.trench_length_m * cross_section * data.trench_depth_m, 3)
    bedding_volume = round(data.trench_length_m * cross_section * bedding_thickness, 3)
    pipe_zone_backfill_volume = round(data.trench_length_m * cross_section * pipe_zone_height, 3)
    remaining_backfill_volume = round(
        max(trench_volume - bedding_volume - pipe_zone_backfill_volume, 0), 3
    )
    excavated_removal_volume = round(trench_volume * (1 + bulking / 100), 3)

    warnings: list[CalculationWarning] = []
    if bedding_thickness + pipe_zone_height > data.trench_depth_m:
        warnings.append(
            CalculationWarning(
                code="zones_exceed_depth",
                message="Bedding + pipe zone exceed trench depth; remaining backfill clamped to 0.",
                severity="warning",
            )
        )
    if data.trench_depth_m > 4:
        warnings.append(
            CalculationWarning(
                code="deep_trench",
                message="Trench depth above 4 m usually requires shoring design.",
                severity="warning",
            )
        )
    if trench_volume == 0:
        warnings.append(
            CalculationWarning(
                code="zero_volume",
                message="Calculated trench volume is zero; check dimensions.",
                severity="error",
            )
        )

    return CalculationResult(
        calculation_type="earthworks_trench",
        steps=[
            CalculationStep(
                label="Trench volume",
                formula="trench_length_m * trench_width_m * trench_depth_m",
                input_values={
                    "trench_length_m": data.trench_length_m,
                    "trench_width_m": data.trench_width_m,
                    "trench_depth_m": data.trench_depth_m,
                },
                result=trench_volume,
                unit="m3",
            ),
            CalculationStep(
                label="Trench length",
                formula="trench_length_m",
                input_values={"trench_length_m": data.trench_length_m},
                result=round(data.trench_length_m, 3),
                unit="m",
            ),
            CalculationStep(
                label="Bedding volume",
                formula="trench_length_m * trench_width_m * bedding_thickness_m",
                input_values={"trench_width_m": data.trench_width_m, "bedding_thickness_m": bedding_thickness},
                result=bedding_volume,
                unit="m3",
            ),
            CalculationStep(
                label="Pipe zone backfill volume",
                formula="trench_length_m * trench_width_m * pipe_zone_height_m",
                input_values={"pipe_zone_height_m": pipe_zone_height},
                result=pipe_zone_backfill_volume,
                unit="m3",
            ),
            CalculationStep(
                label="Remaining backfill volume",
                formula="max(trench_volume - bedding_volume - pipe_zone_backfill_volume, 0)",
                input_values={
                    "trench_volume": trench_volume,
                    "bedding_volume": bedding_volume,
                    "pipe_zone_backfill_volume": pipe_zone_backfill_volume,
                },
                result=remaining_backfill_volume,
                unit="m3",
            ),
        ],
        materials=[
            MaterialItem(name="Trench excavation", quantity=trench_volume, unit="m3"),
            MaterialItem(name="Excavated soil removal (loose)", quantity=excavated_removal_volume, unit="m3"),
            MaterialItem(name="Bedding material", quantity=bedding_volume, unit="m3"),
            MaterialItem(name="Pipe zone backfill", quantity=pipe_zone_backfill_volume, unit="m3"),
            MaterialItem(name="Remaining backfill", quantity=remaining_backfill_volume, unit="m3"),
        ],
        assumptions=[
            CalculationAssumption(
                key="rectangular_section",
                description="Trench is treated as a rectangular prism (vertical walls).",
                source="standard_geometry",
            ),
            CalculationAssumption(
                key="bulking_factor",
                description="Bulking accounts for soil expansion in the removal volume.",
                source="user_input",
            ),
        ],
        warnings=warnings,
    )


def calculate_backfill_v2(data: BackfillInput) -> CalculationResult:
    compaction_factor = data.compaction_factor or 1.0
    waste = data.waste_percent or 0

    compacted_volume = round(data.area_m2 * data.compacted_thickness_m, 3)
    loose_volume_required = round(compacted_volume * compaction_factor, 3)
    material_quantity = round(loose_volume_required * (1 + waste / 100), 3)

    steps = [
        CalculationStep(
            label="Compacted volume",
            formula="area_m2 * compacted_thickness_m",
            input_values={"area_m2": data.area_m2, "compacted_thickness_m": data.compacted_thickness_m},
            result=compacted_volume,
            unit="m3",
        ),
        CalculationStep(
            label="Loose volume required",
            formula="compacted_volume * compaction_factor",
            input_values={"compacted_volume": compacted_volume, "compaction_factor": compaction_factor},
            result=loose_volume_required,
            unit="m3",
        ),
        CalculationStep(
            label="Material quantity with waste",
            formula="loose_volume_required * (1 + waste_percent / 100)",
            input_values={"loose_volume_required": loose_volume_required, "waste_percent": waste},
            result=material_quantity,
            unit="m3",
        ),
    ]

    warnings: list[CalculationWarning] = []
    layer_count = 1.0
    if data.layer_thickness_m is not None:
        layer_count = float(math.ceil(data.compacted_thickness_m / data.layer_thickness_m))
        steps.append(
            CalculationStep(
                label="Layer count",
                formula="ceil(compacted_thickness_m / layer_thickness_m)",
                input_values={
                    "compacted_thickness_m": data.compacted_thickness_m,
                    "layer_thickness_m": data.layer_thickness_m,
                },
                result=layer_count,
                unit="layers",
            )
        )
        if data.layer_thickness_m > data.compacted_thickness_m:
            warnings.append(
                CalculationWarning(
                    code="layer_thicker_than_total",
                    message="Layer thickness exceeds total compacted thickness; single layer assumed.",
                    severity="info",
                )
            )

    if compaction_factor < 1:
        warnings.append(
            CalculationWarning(
                code="compaction_factor_below_one",
                message="Compaction factor below 1 implies less loose material than compacted; verify input.",
                severity="info",
            )
        )

    return CalculationResult(
        calculation_type="earthworks_backfill",
        steps=steps,
        materials=[
            MaterialItem(
                name="Backfill material (loose)",
                quantity=material_quantity,
                unit="m3",
                waste_percent=waste,
            ),
        ],
        assumptions=[
            CalculationAssumption(
                key="compaction_factor",
                description="Loose volume = compacted volume * compaction_factor (default 1.15).",
                source="default" if data.compaction_factor is None else "user_input",
            ),
        ],
        warnings=warnings,
    )
