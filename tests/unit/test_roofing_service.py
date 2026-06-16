import math

import pytest
from pydantic import ValidationError

from app.schemas.roofing import (
    RoofAreaInput,
    RoofCoveringInput,
    RoofGuttersInput,
    RoofInsulationInput,
    RoofMembraneInput,
)
from app.services.roofing_service import (
    calculate_roof_area_v2,
    calculate_roof_covering_v2,
    calculate_roof_gutters_v2,
    calculate_roof_insulation_v2,
    calculate_roof_membrane_v2,
)


def test_roof_area_with_degrees():
    data = RoofAreaInput(length_m=10, width_m=8, slope_degrees=30, waste_percent=0)
    result = calculate_roof_area_v2(data)

    assert result.calculation_type == "roof_area"
    # plan = 80 ; factor = 1/cos(30) ~ 1.1547 ; sloped ~ 92.376
    assert result.steps[0].result == 80
    assert result.steps[2].result == pytest.approx(80 / math.cos(math.radians(30)), rel=1e-3)


def test_roof_area_with_percent():
    data = RoofAreaInput(length_m=10, width_m=10, slope_percent=50, waste_percent=0)
    result = calculate_roof_area_v2(data)
    factor = math.sqrt(1 + 0.5 ** 2)
    assert result.steps[1].result == pytest.approx(factor, rel=1e-4)


def test_roof_area_requires_slope():
    with pytest.raises(ValidationError):
        RoofAreaInput(length_m=10, width_m=8)


def test_roof_covering_sheets_and_fasteners():
    data = RoofCoveringInput(
        roof_area_m2=100, sheet_length_m=2, sheet_width_m=1, overlap_percent=10,
        fasteners_per_m2=6, waste_percent=0,
    )
    result = calculate_roof_covering_v2(data)

    # area with overlap = 110 ; sheets = ceil(110/2) = 55
    sheet_step = next(s for s in result.steps if s.label == "Sheet/tile count")
    assert sheet_step.result == 55
    fasteners = next(m for m in result.materials if m.name == "Fasteners")
    assert fasteners.quantity == 600


def test_roof_membrane_rolls():
    data = RoofMembraneInput(roof_area_m2=100, roll_area_m2=15, overlap_percent=10, waste_percent=0)
    result = calculate_roof_membrane_v2(data)
    roll_step = next(s for s in result.steps if s.label == "Roll count")
    assert roll_step.result == math.ceil(110 / 15)


def test_roof_insulation_volume():
    data = RoofInsulationInput(roof_area_m2=100, thickness_mm=200, waste_percent=0)
    result = calculate_roof_insulation_v2(data)
    vol_step = next(s for s in result.steps if s.label == "Insulation volume")
    assert vol_step.result == pytest.approx(20.0)


def test_roof_gutters_downpipes_and_fittings():
    data = RoofGuttersInput(eaves_length_m=24, downpipe_spacing_m=8, corners_count=4, waste_percent=0)
    result = calculate_roof_gutters_v2(data)

    assert result.calculation_type == "roof_gutters"
    dp_step = next(s for s in result.steps if s.label == "Downpipe count")
    assert dp_step.result == 3  # ceil(24/8)
    fittings = next(m for m in result.materials if m.name == "Fittings")
    assert fittings.quantity == 7  # 4 + 3


def test_roof_gutters_rejects_non_positive():
    with pytest.raises(ValidationError):
        RoofGuttersInput(eaves_length_m=0)
