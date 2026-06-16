import math

import pytest
from pydantic import ValidationError

from app.schemas.floors import FloorInsulationInput, FloorLaminateInput, FloorScreedInput
from app.services.floors_service import (
    calculate_floor_insulation_v2,
    calculate_floor_laminate_v2,
    calculate_floor_screed_v2,
)


def test_floor_screed_volume_and_bags():
    data = FloorScreedInput(
        area_m2=40, thickness_m=0.05, density_kg_per_m3=1800, bag_weight_kg=25, waste_percent=0
    )
    result = calculate_floor_screed_v2(data)

    assert result.calculation_type == "floors_screed"
    # volume = 40 * 0.05 = 2.0
    assert result.steps[0].result == pytest.approx(2.0)
    # dry mix = 2 * 1800 = 3600 ; bags = ceil(3600/25) = 144
    bag_step = next(s for s in result.steps if s.label == "Bag count")
    assert bag_step.result == 144


def test_floor_screed_rejects_non_positive():
    with pytest.raises(ValidationError):
        FloorScreedInput(area_m2=0, thickness_m=0.05)


def test_floor_insulation_boards_and_volume():
    data = FloorInsulationInput(
        area_m2=50, thickness_mm=100, board_length_m=1, board_width_m=0.5, waste_percent=0
    )
    result = calculate_floor_insulation_v2(data)

    assert result.calculation_type == "floors_insulation"
    # volume = 50 * 0.1 = 5.0
    vol_step = next(s for s in result.steps if s.label == "Insulation volume")
    assert vol_step.result == pytest.approx(5.0)
    board_step = next(s for s in result.steps if s.label == "Board count")
    assert board_step.result == math.ceil(50 / 0.5)


def test_floor_insulation_rejects_non_positive():
    with pytest.raises(ValidationError):
        FloorInsulationInput(area_m2=50, thickness_mm=0)


def test_floor_laminate_packs_underlay_baseboard():
    data = FloorLaminateInput(
        area_m2=30, waste_percent=10, pack_area_m2=2.5, perimeter_m=22, openings_width_m=2,
        underlay_enabled=True,
    )
    result = calculate_floor_laminate_v2(data)

    assert result.calculation_type == "floors_laminate"
    # laminate area = 30 * 1.1 = 33 ; packs = ceil(33/2.5) = 14
    pack_step = next(s for s in result.steps if s.label == "Pack count")
    assert pack_step.result == 14
    baseboard = next(m for m in result.materials if m.name == "Baseboard")
    assert baseboard.quantity == pytest.approx(20.0)  # 22 - 2
    assert any(m.name == "Underlay" for m in result.materials)


def test_floor_laminate_rejects_non_positive():
    with pytest.raises(ValidationError):
        FloorLaminateInput(area_m2=0)
