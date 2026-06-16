import math

from app.schemas.rebar import (
    RebarLapLengthInput,
    RebarLinearInput,
    RebarMeshInput,
    RebarStirrupsInput,
)
from app.schemas.calculation_result import (
    CalculationResult,
    CalculationStep,
    CalculationAssumption,
    CalculationWarning,
    MaterialItem,
)

# Standard nominal mass of round steel reinforcement bars.
# weight_per_meter (kg/m) = diameter_mm^2 / 162.
# This matches the existing convention in app/services/bars_calculation and is
# the widely used approximation derived from steel density (~7850 kg/m3):
#   area = pi/4 * (d/1000)^2 [m2]; mass = area * 7850 -> ~= d^2 / 162.
REBAR_WEIGHT_DIVISOR = 162.0


def weight_per_meter_kg(diameter_mm: float) -> float:
    """Return the nominal mass per meter (kg/m) of a round rebar.

    Uses the deterministic d^2 / 162 approximation; no AI is involved.
    """
    return diameter_mm ** 2 / REBAR_WEIGHT_DIVISOR


def calculate_rebar_linear_v2(data: RebarLinearInput) -> CalculationResult:
    length_per_bar = round(data.length_per_bar_m(), 4)
    base_total_length = round(length_per_bar * data.bar_count, 4)

    if data.lap_percent is not None:
        lap_allowance = round(base_total_length * data.lap_percent / 100, 4)
        lap_formula = "base_total_length * lap_percent / 100"
        lap_inputs = {
            "base_total_length": base_total_length,
            "lap_percent": data.lap_percent,
        }
    elif data.lap_length_m is not None:
        lap_allowance = round(data.lap_length_m * data.bar_count, 4)
        lap_formula = "lap_length_m * bar_count"
        lap_inputs = {
            "lap_length_m": data.lap_length_m,
            "bar_count": data.bar_count,
        }
    else:
        lap_allowance = 0.0
        lap_formula = "no lap specified -> 0"
        lap_inputs = {}

    length_with_lap = round(base_total_length + lap_allowance, 4)
    total_length_with_waste = round(length_with_lap * (1 + data.waste_percent / 100), 4)
    per_meter = round(weight_per_meter_kg(data.bar_diameter_mm), 4)
    total_weight = round(total_length_with_waste * per_meter, 4)

    return CalculationResult(
        calculation_type="rebar_linear",
        steps=[
            CalculationStep(
                label="Total bar length (without lap)",
                formula="length_per_bar * bar_count",
                input_values={
                    "length_per_bar": length_per_bar,
                    "bar_count": data.bar_count,
                },
                result=base_total_length,
                unit="m",
            ),
            CalculationStep(
                label="Lap/overlap allowance",
                formula=lap_formula,
                input_values=lap_inputs,
                result=lap_allowance,
                unit="m",
            ),
            CalculationStep(
                label="Total length with lap",
                formula="base_total_length + lap_allowance",
                input_values={
                    "base_total_length": base_total_length,
                    "lap_allowance": lap_allowance,
                },
                result=length_with_lap,
                unit="m",
            ),
            CalculationStep(
                label="Total length with waste",
                formula="length_with_lap * (1 + waste_percent / 100)",
                input_values={
                    "length_with_lap": length_with_lap,
                    "waste_percent": data.waste_percent,
                },
                result=total_length_with_waste,
                unit="m",
            ),
            CalculationStep(
                label="Weight per meter",
                formula="bar_diameter_mm^2 / 162",
                input_values={"bar_diameter_mm": data.bar_diameter_mm},
                result=per_meter,
                unit="kg/m",
            ),
            CalculationStep(
                label="Total rebar weight",
                formula="total_length_with_waste * weight_per_meter",
                input_values={
                    "total_length_with_waste": total_length_with_waste,
                    "weight_per_meter": per_meter,
                },
                result=total_weight,
                unit="kg",
            ),
        ],
        materials=[
            MaterialItem(
                name=f"Rebar D{int(data.bar_diameter_mm)}mm"
                if float(data.bar_diameter_mm).is_integer()
                else f"Rebar D{data.bar_diameter_mm}mm",
                quantity=total_weight,
                unit="kg",
                waste_percent=data.waste_percent,
            ),
            MaterialItem(
                name=f"Rebar D{int(data.bar_diameter_mm)}mm (length)"
                if float(data.bar_diameter_mm).is_integer()
                else f"Rebar D{data.bar_diameter_mm}mm (length)",
                quantity=total_length_with_waste,
                unit="m",
                waste_percent=data.waste_percent,
            ),
        ],
        assumptions=_build_rebar_assumptions(data),
        warnings=_build_rebar_warnings(data, base_total_length),
    )


def _build_rebar_assumptions(data: RebarLinearInput) -> list[CalculationAssumption]:
    assumptions = [
        CalculationAssumption(
            key="weight_formula",
            description="Rebar mass per meter uses the nominal steel formula diameter_mm^2 / 162.",
            source="standard_steel_formula",
        ),
        CalculationAssumption(
            key="waste_percent",
            description="Waste/cutting reserve is based on input waste_percent.",
            source="user_input",
        ),
    ]
    if data.lap_percent is None and data.lap_length_m is None:
        assumptions.append(
            CalculationAssumption(
                key="lap_allowance",
                description="No lap/overlap was provided; lap allowance is treated as zero.",
                source="default",
            )
        )
    return assumptions


def _build_rebar_warnings(
    data: RebarLinearInput,
    base_total_length: float,
) -> list[CalculationWarning]:
    warnings: list[CalculationWarning] = []

    if data.lap_percent is None and data.lap_length_m is None:
        warnings.append(
            CalculationWarning(
                code="no_lap_specified",
                message="No lap/overlap allowance was specified; splices are not accounted for.",
                severity="info",
            )
        )

    if data.waste_percent > 25:
        warnings.append(
            CalculationWarning(
                code="high_waste_percent",
                message="Waste percentage is above 25%, which may indicate a conservative estimate.",
                severity="info",
            )
        )

    if data.bar_diameter_mm > 40:
        warnings.append(
            CalculationWarning(
                code="large_bar_diameter",
                message="Bar diameter is unusually large (>40 mm); verify the input.",
                severity="warning",
            )
        )

    if base_total_length == 0:
        warnings.append(
            CalculationWarning(
                code="zero_length",
                message="Calculated total bar length is zero; check input values.",
                severity="error",
            )
        )

    return warnings


def calculate_rebar_mesh_v2(data: RebarMeshInput) -> CalculationResult:
    overlap = data.overlap_percent or 0
    waste = data.waste_percent or 0

    mesh_area = round(data.area_m2, 4)
    sheet_area = round(data.sheet_length_m * data.sheet_width_m, 4)
    area_with_overlap = round(mesh_area * (1 + overlap / 100), 4)
    overlap_area = round(area_with_overlap - mesh_area, 4)
    area_with_waste = round(area_with_overlap * (1 + waste / 100), 4)
    sheet_count = float(math.ceil(area_with_waste / sheet_area))

    steps = [
        CalculationStep(
            label="Mesh area",
            formula="area_m2",
            input_values={"area_m2": data.area_m2},
            result=mesh_area,
            unit="m2",
        ),
        CalculationStep(
            label="Area with overlap",
            formula="mesh_area * (1 + overlap_percent / 100)",
            input_values={"mesh_area": mesh_area, "overlap_percent": overlap},
            result=area_with_overlap,
            unit="m2",
        ),
        CalculationStep(
            label="Overlap area",
            formula="area_with_overlap - mesh_area",
            input_values={"area_with_overlap": area_with_overlap, "mesh_area": mesh_area},
            result=overlap_area,
            unit="m2",
        ),
        CalculationStep(
            label="Total mesh area with waste",
            formula="area_with_overlap * (1 + waste_percent / 100)",
            input_values={"area_with_overlap": area_with_overlap, "waste_percent": waste},
            result=area_with_waste,
            unit="m2",
        ),
        CalculationStep(
            label="Number of mesh sheets",
            formula="ceil(area_with_waste / (sheet_length_m * sheet_width_m))",
            input_values={"area_with_waste": area_with_waste, "sheet_area": sheet_area},
            result=sheet_count,
            unit="pcs",
        ),
    ]

    materials = [
        MaterialItem(name="Mesh sheets", quantity=sheet_count, unit="pcs", waste_percent=waste),
        MaterialItem(name="Mesh area", quantity=area_with_waste, unit="m2", waste_percent=waste),
    ]

    if data.kg_per_m2 is not None:
        weight = round(area_with_waste * data.kg_per_m2, 2)
        steps.append(
            CalculationStep(
                label="Mesh weight estimate",
                formula="area_with_waste * kg_per_m2",
                input_values={"area_with_waste": area_with_waste, "kg_per_m2": data.kg_per_m2},
                result=weight,
                unit="kg",
            )
        )
        materials.append(MaterialItem(name="Mesh (weight)", quantity=weight, unit="kg"))

    return CalculationResult(
        calculation_type="rebar_mesh",
        steps=steps,
        materials=materials,
        assumptions=[
            CalculationAssumption(
                key="overlap_allowance",
                description="Overlap is added as a percentage of base area; sheet count is rounded up.",
                source="user_input",
            ),
        ],
        warnings=[],
    )


def calculate_rebar_stirrups_v2(data: RebarStirrupsInput) -> CalculationResult:
    waste = data.waste_percent or 0
    hook_length = data.hook_length_m or 0

    stirrup_count = float(math.floor(data.beam_length_m / data.spacing_m) + 1)
    length_per_stirrup = round(
        2 * (data.stirrup_width_m + data.stirrup_height_m) + 2 * hook_length, 4
    )
    total_length = round(stirrup_count * length_per_stirrup * (1 + waste / 100), 4)
    per_meter = round(weight_per_meter_kg(data.bar_diameter_mm), 4)
    total_weight = round(total_length * per_meter, 4)

    return CalculationResult(
        calculation_type="rebar_stirrups",
        steps=[
            CalculationStep(
                label="Stirrup count",
                formula="floor(beam_length_m / spacing_m) + 1",
                input_values={"beam_length_m": data.beam_length_m, "spacing_m": data.spacing_m},
                result=stirrup_count,
                unit="pcs",
            ),
            CalculationStep(
                label="Length per stirrup",
                formula="2 * (stirrup_width_m + stirrup_height_m) + 2 * hook_length_m",
                input_values={
                    "stirrup_width_m": data.stirrup_width_m,
                    "stirrup_height_m": data.stirrup_height_m,
                    "hook_length_m": hook_length,
                },
                result=length_per_stirrup,
                unit="m",
            ),
            CalculationStep(
                label="Total rebar length (with waste)",
                formula="stirrup_count * length_per_stirrup * (1 + waste_percent / 100)",
                input_values={
                    "stirrup_count": stirrup_count,
                    "length_per_stirrup": length_per_stirrup,
                    "waste_percent": waste,
                },
                result=total_length,
                unit="m",
            ),
            CalculationStep(
                label="Total rebar weight",
                formula="total_length * (bar_diameter_mm^2 / 162)",
                input_values={"total_length": total_length, "weight_per_meter": per_meter},
                result=total_weight,
                unit="kg",
            ),
        ],
        materials=[
            MaterialItem(
                name=f"Stirrup rebar D{int(data.bar_diameter_mm)}mm"
                if float(data.bar_diameter_mm).is_integer()
                else f"Stirrup rebar D{data.bar_diameter_mm}mm",
                quantity=total_weight,
                unit="kg",
                waste_percent=waste,
            ),
            MaterialItem(name="Stirrup rebar (length)", quantity=total_length, unit="m", waste_percent=waste),
        ],
        assumptions=[
            CalculationAssumption(
                key="stirrup_count_method",
                description="Stirrup count = floor(beam_length / spacing) + 1 (end stirrup included).",
                source="standard_practice",
            ),
            CalculationAssumption(
                key="weight_formula",
                description="Rebar mass per meter uses diameter_mm^2 / 162.",
                source="standard_steel_formula",
            ),
        ],
        warnings=[],
    )


def calculate_rebar_lap_length_v2(data: RebarLapLengthInput) -> CalculationResult:
    lap_multiplier = data.lap_multiplier or 40
    laps_per_bar = data.laps_per_bar if data.laps_per_bar is not None else 1

    lap_length_m = round(lap_multiplier * data.bar_diameter_mm / 1000, 4)
    total_overlap_length = round(lap_length_m * data.bar_count * laps_per_bar, 4)

    warnings: list[CalculationWarning] = []
    if laps_per_bar == 0:
        warnings.append(
            CalculationWarning(
                code="no_laps",
                message="laps_per_bar is 0; total overlap length is zero.",
                severity="info",
            )
        )

    return CalculationResult(
        calculation_type="rebar_lap_length",
        steps=[
            CalculationStep(
                label="Lap length per splice",
                formula="lap_multiplier * bar_diameter_mm / 1000",
                input_values={"lap_multiplier": lap_multiplier, "bar_diameter_mm": data.bar_diameter_mm},
                result=lap_length_m,
                unit="m",
            ),
            CalculationStep(
                label="Total overlap length",
                formula="lap_length_m * bar_count * laps_per_bar",
                input_values={
                    "lap_length_m": lap_length_m,
                    "bar_count": data.bar_count,
                    "laps_per_bar": laps_per_bar,
                },
                result=total_overlap_length,
                unit="m",
            ),
        ],
        materials=[
            MaterialItem(name="Lap overlap (extra rebar length)", quantity=total_overlap_length, unit="m"),
        ],
        assumptions=[
            CalculationAssumption(
                key="lap_multiplier",
                description="Lap length = lap_multiplier * bar diameter (default 40d); confirm against the project code/standard.",
                source="default" if data.lap_multiplier is None else "user_input",
            ),
        ],
        warnings=warnings,
    )
