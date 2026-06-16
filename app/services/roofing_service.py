import math

from app.schemas.roofing import (
    RoofAreaInput,
    RoofCoveringInput,
    RoofGuttersInput,
    RoofInsulationInput,
    RoofMembraneInput,
)
from app.schemas.calculation_result import (
    CalculationResult,
    CalculationStep,
    CalculationAssumption,
    CalculationWarning,
    MaterialItem,
)


def calculate_roof_area_v2(data: RoofAreaInput) -> CalculationResult:
    waste = data.waste_percent or 0
    plan_area = round(data.length_m * data.width_m, 3)

    if data.slope_degrees is not None:
        slope_factor = 1 / math.cos(math.radians(data.slope_degrees))
        slope_formula = "1 / cos(slope_degrees)"
        slope_inputs = {"slope_degrees": data.slope_degrees}
    else:
        slope_factor = math.sqrt(1 + (data.slope_percent / 100) ** 2)
        slope_formula = "sqrt(1 + (slope_percent / 100)^2)"
        slope_inputs = {"slope_percent": data.slope_percent}

    slope_factor = round(slope_factor, 5)
    sloped_area = round(plan_area * slope_factor, 3)
    area_with_waste = round(sloped_area * (1 + waste / 100), 3)

    return CalculationResult(
        calculation_type="roof_area",
        steps=[
            CalculationStep(
                label="Plan area",
                formula="length_m * width_m",
                input_values={"length_m": data.length_m, "width_m": data.width_m},
                result=plan_area,
                unit="m2",
            ),
            CalculationStep(
                label="Slope factor",
                formula=slope_formula,
                input_values=slope_inputs,
                result=slope_factor,
                unit="ratio",
            ),
            CalculationStep(
                label="Sloped roof area",
                formula="plan_area * slope_factor",
                input_values={"plan_area": plan_area, "slope_factor": slope_factor},
                result=sloped_area,
                unit="m2",
            ),
            CalculationStep(
                label="Roof area with waste",
                formula="sloped_area * (1 + waste_percent / 100)",
                input_values={"sloped_area": sloped_area, "waste_percent": waste},
                result=area_with_waste,
                unit="m2",
            ),
        ],
        materials=[
            MaterialItem(name="Roof area", quantity=area_with_waste, unit="m2", waste_percent=waste),
        ],
        assumptions=[
            CalculationAssumption(
                key="slope_factor",
                description="Sloped area = plan area divided by cosine of pitch; plan area is the building footprint.",
                source="standard_geometry",
            ),
        ],
        warnings=[],
    )


def calculate_roof_covering_v2(data: RoofCoveringInput) -> CalculationResult:
    overlap = data.overlap_percent or 0
    waste = data.waste_percent or 0
    area_with_overlap = round(data.roof_area_m2 * (1 + overlap / 100), 3)
    area_with_waste = round(area_with_overlap * (1 + waste / 100), 3)

    steps = [
        CalculationStep(
            label="Area with overlap",
            formula="roof_area_m2 * (1 + overlap_percent / 100)",
            input_values={"roof_area_m2": data.roof_area_m2, "overlap_percent": overlap},
            result=area_with_overlap,
            unit="m2",
        ),
        CalculationStep(
            label="Covering area with waste",
            formula="area_with_overlap * (1 + waste_percent / 100)",
            input_values={"area_with_overlap": area_with_overlap, "waste_percent": waste},
            result=area_with_waste,
            unit="m2",
        ),
    ]
    materials = [
        MaterialItem(name="Roof covering", quantity=area_with_waste, unit="m2", waste_percent=waste),
    ]

    if data.sheet_length_m is not None and data.sheet_width_m is not None:
        sheet_area = data.sheet_length_m * data.sheet_width_m
        sheet_count = float(math.ceil(area_with_waste / sheet_area))
        steps.append(
            CalculationStep(
                label="Sheet/tile count",
                formula="ceil(area_with_waste / (sheet_length_m * sheet_width_m))",
                input_values={"area_with_waste": area_with_waste, "sheet_area": round(sheet_area, 4)},
                result=sheet_count,
                unit="pcs",
            )
        )
        materials.append(MaterialItem(name="Roof sheets/tiles", quantity=sheet_count, unit="pcs"))

    if data.fasteners_per_m2 is not None:
        fasteners = float(math.ceil(data.roof_area_m2 * data.fasteners_per_m2))
        steps.append(
            CalculationStep(
                label="Fasteners",
                formula="ceil(roof_area_m2 * fasteners_per_m2)",
                input_values={"roof_area_m2": data.roof_area_m2, "fasteners_per_m2": data.fasteners_per_m2},
                result=fasteners,
                unit="pcs",
            )
        )
        materials.append(MaterialItem(name="Fasteners", quantity=fasteners, unit="pcs"))

    return CalculationResult(
        calculation_type="roof_covering",
        steps=steps,
        materials=materials,
        assumptions=[
            CalculationAssumption(
                key="overlap_allowance",
                description="Overlap is added as a percentage of roof area before waste.",
                source="user_input",
            ),
        ],
        warnings=[],
    )


def calculate_roof_membrane_v2(data: RoofMembraneInput) -> CalculationResult:
    overlap = data.overlap_percent or 0
    waste = data.waste_percent or 0
    area_with_overlap = round(data.roof_area_m2 * (1 + overlap / 100), 3)
    area_with_waste = round(area_with_overlap * (1 + waste / 100), 3)

    steps = [
        CalculationStep(
            label="Area with overlap",
            formula="roof_area_m2 * (1 + overlap_percent / 100)",
            input_values={"roof_area_m2": data.roof_area_m2, "overlap_percent": overlap},
            result=area_with_overlap,
            unit="m2",
        ),
        CalculationStep(
            label="Membrane area with waste",
            formula="area_with_overlap * (1 + waste_percent / 100)",
            input_values={"area_with_overlap": area_with_overlap, "waste_percent": waste},
            result=area_with_waste,
            unit="m2",
        ),
    ]
    materials = [
        MaterialItem(name="Roof membrane", quantity=area_with_waste, unit="m2", waste_percent=waste),
    ]

    if data.roll_area_m2 is not None:
        roll_count = float(math.ceil(area_with_waste / data.roll_area_m2))
        steps.append(
            CalculationStep(
                label="Roll count",
                formula="ceil(area_with_waste / roll_area_m2)",
                input_values={"area_with_waste": area_with_waste, "roll_area_m2": data.roll_area_m2},
                result=roll_count,
                unit="rolls",
            )
        )
        materials.append(MaterialItem(name="Membrane rolls", quantity=roll_count, unit="rolls"))

    return CalculationResult(
        calculation_type="roof_membrane",
        steps=steps,
        materials=materials,
        assumptions=[
            CalculationAssumption(
                key="overlap_allowance",
                description="Membrane overlap is added as a percentage of roof area.",
                source="user_input",
            ),
        ],
        warnings=[],
    )


def calculate_roof_insulation_v2(data: RoofInsulationInput) -> CalculationResult:
    waste = data.waste_percent or 0
    area_with_waste = round(data.roof_area_m2 * (1 + waste / 100), 3)
    volume = round(data.roof_area_m2 * data.thickness_mm / 1000, 4)

    steps = [
        CalculationStep(
            label="Insulation area with waste",
            formula="roof_area_m2 * (1 + waste_percent / 100)",
            input_values={"roof_area_m2": data.roof_area_m2, "waste_percent": waste},
            result=area_with_waste,
            unit="m2",
        ),
        CalculationStep(
            label="Insulation volume",
            formula="roof_area_m2 * thickness_mm / 1000",
            input_values={"roof_area_m2": data.roof_area_m2, "thickness_mm": data.thickness_mm},
            result=volume,
            unit="m3",
        ),
    ]
    materials = [
        MaterialItem(name="Roof insulation", quantity=area_with_waste, unit="m2", waste_percent=waste),
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
        calculation_type="roof_insulation",
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


def calculate_roof_gutters_v2(data: RoofGuttersInput) -> CalculationResult:
    waste = data.waste_percent or 0
    spacing = data.downpipe_spacing_m or 10
    corners = data.corners_count or 0

    gutter_length = round(data.eaves_length_m * (1 + waste / 100), 3)
    downpipe_count = float(math.ceil(data.eaves_length_m / spacing))
    fittings_count = float(corners + int(downpipe_count))

    return CalculationResult(
        calculation_type="roof_gutters",
        steps=[
            CalculationStep(
                label="Gutter length (with waste)",
                formula="eaves_length_m * (1 + waste_percent / 100)",
                input_values={"eaves_length_m": data.eaves_length_m, "waste_percent": waste},
                result=gutter_length,
                unit="m",
            ),
            CalculationStep(
                label="Downpipe count",
                formula="ceil(eaves_length_m / downpipe_spacing_m)",
                input_values={"eaves_length_m": data.eaves_length_m, "downpipe_spacing_m": spacing},
                result=downpipe_count,
                unit="pcs",
            ),
            CalculationStep(
                label="Fittings (approximate)",
                formula="corners_count + downpipe_count",
                input_values={"corners_count": corners, "downpipe_count": downpipe_count},
                result=fittings_count,
                unit="pcs",
            ),
        ],
        materials=[
            MaterialItem(name="Gutters", quantity=gutter_length, unit="m", waste_percent=waste),
            MaterialItem(name="Downpipes", quantity=downpipe_count, unit="pcs"),
            MaterialItem(name="Fittings", quantity=fittings_count, unit="pcs"),
        ],
        assumptions=[
            CalculationAssumption(
                key="downpipe_spacing",
                description="Downpipe count assumes a default spacing of 10 m unless provided.",
                source="default" if data.downpipe_spacing_m is None else "user_input",
            ),
            CalculationAssumption(
                key="fittings_estimate",
                description="Fittings are a rough sum of corners and downpipe outlets.",
                source="approximate",
            ),
        ],
        warnings=[
            CalculationWarning(
                code="approximate_fittings",
                message="Gutter fittings are approximate; confirm against the manufacturer's system components.",
                severity="info",
            ),
        ],
    )
