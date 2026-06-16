import math

import pytest
from pydantic import ValidationError

from app.schemas.rebar import (
    RebarLapLengthInput,
    RebarLinearInput,
    RebarMeshInput,
    RebarStirrupsInput,
)
from app.services.rebar_service import (
    calculate_rebar_lap_length_v2,
    calculate_rebar_linear_v2,
    calculate_rebar_mesh_v2,
    calculate_rebar_stirrups_v2,
    weight_per_meter_kg,
)


def test_weight_per_meter_uses_standard_formula():
    # 12 mm rebar -> 12^2 / 162 = 0.888... kg/m
    assert weight_per_meter_kg(12) == pytest.approx(144 / 162)


def test_calculate_rebar_linear_v2_basic_shape_and_values():
    data = RebarLinearInput(
        total_length_m=10,
        bar_diameter_mm=12,
        bar_count=4,
        waste_percent=0,
    )

    result = calculate_rebar_linear_v2(data)

    assert result.calculation_type == "rebar_linear"
    # base length = 10 * 4 = 40, no lap, no waste
    base_step = result.steps[0]
    assert base_step.result == 40
    # total weight = 40 * round(144/162, 4); per-meter weight is rounded first
    per_meter = round(144 / 162, 4)
    assert result.materials[0].unit == "kg"
    assert result.materials[0].quantity == pytest.approx(round(40 * per_meter, 4))
    assert result.materials[1].unit == "m"
    assert result.materials[1].quantity == 40
    assert result.assumptions  # not empty
    # no lap specified -> info warning present
    assert any(w.code == "no_lap_specified" for w in result.warnings)


def test_rebar_linear_segment_lengths_are_summed():
    data = RebarLinearInput(
        segment_lengths_m=[3, 3, 4],
        bar_diameter_mm=10,
        bar_count=2,
        waste_percent=0,
    )

    result = calculate_rebar_linear_v2(data)

    # (3+3+4) * 2 = 20
    assert result.steps[0].result == 20


def test_rebar_linear_lap_percent_applied():
    data = RebarLinearInput(
        total_length_m=10,
        bar_diameter_mm=12,
        bar_count=2,
        lap_percent=10,
        waste_percent=0,
    )

    result = calculate_rebar_linear_v2(data)

    lap_step = result.steps[1]
    assert lap_step.result == pytest.approx(2.0)  # 20 * 10%
    assert result.steps[2].result == pytest.approx(22.0)


def test_rebar_linear_lap_length_applied_per_bar():
    data = RebarLinearInput(
        total_length_m=10,
        bar_diameter_mm=12,
        bar_count=3,
        lap_length_m=0.5,
        waste_percent=0,
    )

    result = calculate_rebar_linear_v2(data)

    lap_step = result.steps[1]
    assert lap_step.result == pytest.approx(1.5)  # 0.5 * 3


def test_rebar_linear_waste_applied():
    data = RebarLinearInput(
        total_length_m=10,
        bar_diameter_mm=12,
        bar_count=2,
        waste_percent=10,
    )

    result = calculate_rebar_linear_v2(data)

    # length with waste = 20 * 1.10 = 22
    assert result.steps[3].result == pytest.approx(22.0)


def test_rebar_linear_warns_on_high_waste_and_large_diameter():
    data = RebarLinearInput(
        total_length_m=10,
        bar_diameter_mm=50,
        bar_count=2,
        lap_percent=5,
        waste_percent=30,
    )

    result = calculate_rebar_linear_v2(data)

    codes = {w.code for w in result.warnings}
    assert "high_waste_percent" in codes
    assert "large_bar_diameter" in codes


def test_rebar_input_requires_length_source():
    with pytest.raises(ValidationError):
        RebarLinearInput(bar_diameter_mm=12, bar_count=4)


def test_rebar_input_rejects_non_positive_values():
    with pytest.raises(ValidationError):
        RebarLinearInput(total_length_m=-1, bar_diameter_mm=12, bar_count=4)
    with pytest.raises(ValidationError):
        RebarLinearInput(total_length_m=10, bar_diameter_mm=0, bar_count=4)
    with pytest.raises(ValidationError):
        RebarLinearInput(total_length_m=10, bar_diameter_mm=12, bar_count=0)


def test_rebar_input_rejects_negative_waste():
    with pytest.raises(ValidationError):
        RebarLinearInput(
            total_length_m=10,
            bar_diameter_mm=12,
            bar_count=4,
            waste_percent=-5,
        )


def test_rebar_mesh_sheets_and_overlap():
    data = RebarMeshInput(
        area_m2=100, sheet_length_m=2, sheet_width_m=1, overlap_percent=10, waste_percent=0, kg_per_m2=3
    )
    result = calculate_rebar_mesh_v2(data)

    assert result.calculation_type == "rebar_mesh"
    # area with overlap = 110, overlap area = 10
    assert result.steps[1].result == pytest.approx(110.0)
    assert result.steps[2].result == pytest.approx(10.0)
    # sheets = ceil(110 / 2) = 55
    sheet_step = next(s for s in result.steps if s.label == "Number of mesh sheets")
    assert sheet_step.result == 55
    weight = next(m for m in result.materials if m.name == "Mesh (weight)")
    assert weight.quantity == pytest.approx(330.0)  # 110 * 3


def test_rebar_mesh_rejects_non_positive():
    with pytest.raises(ValidationError):
        RebarMeshInput(area_m2=0, sheet_length_m=2, sheet_width_m=1)


def test_rebar_stirrups_count_and_weight():
    data = RebarStirrupsInput(
        beam_length_m=10, spacing_m=0.2, stirrup_width_m=0.3, stirrup_height_m=0.5,
        bar_diameter_mm=8, hook_length_m=0.1, waste_percent=0,
    )
    result = calculate_rebar_stirrups_v2(data)

    assert result.calculation_type == "rebar_stirrups"
    # count = floor(10/0.2)+1 = 51
    assert result.steps[0].result == 51
    # length per stirrup = 2*(0.3+0.5)+2*0.1 = 1.8
    assert result.steps[1].result == pytest.approx(1.8)
    assert any(m.unit == "kg" for m in result.materials)


def test_rebar_stirrups_rejects_non_positive():
    with pytest.raises(ValidationError):
        RebarStirrupsInput(
            beam_length_m=10, spacing_m=0, stirrup_width_m=0.3, stirrup_height_m=0.5, bar_diameter_mm=8
        )


def test_rebar_lap_length_values():
    data = RebarLapLengthInput(bar_diameter_mm=12, bar_count=20, lap_multiplier=40, laps_per_bar=1)
    result = calculate_rebar_lap_length_v2(data)

    assert result.calculation_type == "rebar_lap_length"
    # lap = 40 * 12 / 1000 = 0.48
    assert result.steps[0].result == pytest.approx(0.48)
    # total = 0.48 * 20 * 1 = 9.6
    assert result.steps[1].result == pytest.approx(9.6)
    assert result.materials


def test_rebar_lap_length_rejects_non_positive():
    with pytest.raises(ValidationError):
        RebarLapLengthInput(bar_diameter_mm=12, bar_count=0)
