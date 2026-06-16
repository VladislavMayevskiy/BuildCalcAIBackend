import math

import pytest
from pydantic import ValidationError

from app.schemas.tiles import (
    TilesAdhesiveInput,
    TilesFloorInput,
    TilesGroutInput,
    TilesWallInput,
)
from app.services.tiles_service import (
    calculate_tiles_adhesive_v2,
    calculate_tiles_floor_v2,
    calculate_tiles_grout_v2,
    calculate_tiles_wall_v2,
)


def test_tiles_floor_count_and_extras():
    data = TilesFloorInput(
        area_m2=20, tile_length_m=0.6, tile_width_m=0.6, waste_percent=10,
        adhesive_kg_per_m2=4, grout_kg_per_m2=0.5, pack_area_m2=1.44,
    )
    result = calculate_tiles_floor_v2(data)

    assert result.calculation_type == "tiles_floor"
    # area with waste = 22 ; tile area = 0.36 ; count = ceil(22/0.36)=62
    count_step = next(s for s in result.steps if s.label == "Tile count")
    assert count_step.result == math.ceil(22 / 0.36)
    assert any(m.name == "Tile adhesive" for m in result.materials)
    assert any(m.name == "Grout" for m in result.materials)


def test_tiles_floor_rejects_non_positive():
    with pytest.raises(ValidationError):
        TilesFloorInput(area_m2=0, tile_length_m=0.6, tile_width_m=0.6)


def test_tiles_wall_net_area_and_warning():
    data = TilesWallInput(
        gross_area_m2=30, openings_area_m2=5, tile_length_m=0.3, tile_width_m=0.3, waste_percent=0
    )
    result = calculate_tiles_wall_v2(data)

    net_step = next(s for s in result.steps if s.label == "Net tiled area")
    assert net_step.result == 25
    assert result.calculation_type == "tiles_wall"


def test_tiles_wall_warns_on_zero_net():
    data = TilesWallInput(
        gross_area_m2=4, openings_area_m2=10, tile_length_m=0.3, tile_width_m=0.3
    )
    result = calculate_tiles_wall_v2(data)
    assert any(w.code == "zero_net_area" for w in result.warnings)


def test_tiles_adhesive_bags():
    data = TilesAdhesiveInput(area_m2=20, adhesive_kg_per_m2=4, bag_weight_kg=25, waste_percent=0)
    result = calculate_tiles_adhesive_v2(data)

    # adhesive = 80 kg ; bags = ceil(80/25)=4
    assert result.steps[0].result == pytest.approx(80.0)
    bag_step = next(s for s in result.steps if s.label == "Bag count")
    assert bag_step.result == 4


def test_tiles_adhesive_rejects_non_positive():
    with pytest.raises(ValidationError):
        TilesAdhesiveInput(area_m2=0, adhesive_kg_per_m2=4, bag_weight_kg=25)


def test_tiles_grout_quantity_and_warning():
    data = TilesGroutInput(area_m2=20, grout_kg_per_m2=0.5, bag_weight_kg=5, waste_percent=0)
    result = calculate_tiles_grout_v2(data)

    assert result.steps[0].result == pytest.approx(10.0)
    assert any(w.code == "approximate_grout" for w in result.warnings)


def test_tiles_grout_rejects_non_positive_rate():
    with pytest.raises(ValidationError):
        TilesGroutInput(area_m2=20, grout_kg_per_m2=0)
