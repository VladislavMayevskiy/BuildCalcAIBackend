import math

import pytest
from pydantic import ValidationError

from app.schemas.facade import (
    FacadeAreaInput,
    FacadeInsulationInput,
    FacadePaintInput,
    FacadePlasterInput,
)
from app.services.facade_service import (
    calculate_facade_area_v2,
    calculate_facade_insulation_v2,
    calculate_facade_paint_v2,
    calculate_facade_plaster_v2,
)


def test_facade_area_net_and_waste():
    data = FacadeAreaInput(
        facades=[{"width_m": 10, "height_m": 3}, {"width_m": 8, "height_m": 3}],
        openings_area_m2=10,
        waste_percent=5,
    )
    result = calculate_facade_area_v2(data)

    assert result.calculation_type == "facade_area"
    # gross = 30 + 24 = 54; net = 44; with waste = 46.2
    assert result.steps[0].result == 54
    assert result.steps[2].result == 44
    assert result.steps[3].result == pytest.approx(46.2)


def test_facade_area_warns_on_zero_net():
    data = FacadeAreaInput(facades=[{"width_m": 2, "height_m": 2}], openings_area_m2=10)
    result = calculate_facade_area_v2(data)
    assert any(w.code == "zero_net_area" for w in result.warnings)


def test_facade_area_requires_panels():
    with pytest.raises(ValidationError):
        FacadeAreaInput(facades=[])


def test_facade_insulation_counts():
    data = FacadeInsulationInput(
        area_m2=100, board_length_m=1, board_width_m=0.5,
        adhesive_coverage_m2_per_bag=4, dowels_per_m2=6, mesh_overlap_percent=10, waste_percent=0,
    )
    result = calculate_facade_insulation_v2(data)

    assert result.calculation_type == "facade_insulation"
    board_step = next(s for s in result.steps if s.label == "Board count")
    assert board_step.result == math.ceil(100 / 0.5)
    dowels = next(m for m in result.materials if m.name == "Dowels")
    assert dowels.quantity == 600  # ceil(100*6)
    mesh = next(m for m in result.materials if m.name == "Reinforcing mesh")
    assert mesh.quantity == pytest.approx(110.0)


def test_facade_insulation_rejects_non_positive():
    with pytest.raises(ValidationError):
        FacadeInsulationInput(area_m2=0, board_length_m=1, board_width_m=0.5)


def test_facade_plaster_quantity():
    data = FacadePlasterInput(area_m2=100, plaster_kg_per_m2=2, primer_coverage_m2_per_l=10, waste_percent=0)
    result = calculate_facade_plaster_v2(data)

    assert result.steps[1].result == pytest.approx(200.0)
    primer = next(m for m in result.materials if m.name == "Primer")
    assert primer.quantity == pytest.approx(10.0)


def test_facade_paint_quantity_with_coats():
    data = FacadePaintInput(area_m2=100, paint_coverage_m2_per_l=10, coats_count=2, waste_percent=0)
    result = calculate_facade_paint_v2(data)

    # paint = 100 * 2 / 10 = 20
    assert result.steps[1].result == pytest.approx(20.0)
    assert result.materials[0].name == "Paint"


def test_facade_paint_rejects_non_positive():
    with pytest.raises(ValidationError):
        FacadePaintInput(area_m2=0, paint_coverage_m2_per_l=10, coats_count=2)
