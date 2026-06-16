import math

import pytest
from pydantic import ValidationError

from app.schemas.walls import WallBlocksInput, WallBricksInput, WallMortarInput
from app.services.walls_service import (
    calculate_wall_blocks_v2,
    calculate_wall_bricks_v2,
    calculate_wall_mortar_v2,
)


def test_wall_blocks_net_area_and_count():
    data = WallBlocksInput(
        wall_length_m=10, wall_height_m=3, openings_area_m2=6,
        block_length_m=0.6, block_height_m=0.2, joint_thickness_m=0, waste_percent=0,
    )
    result = calculate_wall_blocks_v2(data)

    assert result.calculation_type == "walls_blocks"
    # gross 30, openings 6, net 24
    net_step = next(s for s in result.steps if s.label == "Net wall area")
    assert net_step.result == 24
    # block face = 0.6*0.2 = 0.12 -> per m2 = 8.333 ; count = 24*8.333=200
    count_step = next(s for s in result.steps if s.label == "Block count with waste")
    assert count_step.result == 200
    assert result.materials[0].name == "Blocks"


def test_wall_blocks_warns_on_zero_net_area():
    data = WallBlocksInput(
        wall_length_m=2, wall_height_m=2, openings_area_m2=10,
        block_length_m=0.6, block_height_m=0.2,
    )
    result = calculate_wall_blocks_v2(data)
    assert any(w.code == "zero_net_area" for w in result.warnings)


def test_wall_blocks_rejects_non_positive():
    with pytest.raises(ValidationError):
        WallBlocksInput(wall_length_m=0, wall_height_m=3, block_length_m=0.6, block_height_m=0.2)


def test_wall_bricks_count_and_mortar():
    data = WallBricksInput(
        wall_length_m=10, wall_height_m=3, brick_length_m=0.25, brick_height_m=0.065,
        brick_width_m=0.12, joint_thickness_m=0, wall_thickness_bricks=1, waste_percent=0,
    )
    result = calculate_wall_bricks_v2(data)

    assert result.calculation_type == "walls_bricks"
    mortar = next(m for m in result.materials if m.name == "Mortar")
    assert mortar.unit == "m3"
    assert any(m.name == "Bricks" for m in result.materials)


def test_wall_bricks_rejects_non_positive():
    with pytest.raises(ValidationError):
        WallBricksInput(wall_length_m=10, wall_height_m=3, brick_length_m=0, brick_height_m=0.065)


def test_wall_mortar_with_rate_and_bags():
    data = WallMortarInput(
        masonry_area_m2=50, wall_thickness_m=0.25, mortar_rate_m3_per_m2=0.02,
        dry_mix_kg_per_m3=1600, bag_weight_kg=25, waste_percent=0,
    )
    result = calculate_wall_mortar_v2(data)

    assert result.calculation_type == "walls_mortar"
    # volume = 50*0.02 = 1.0
    assert result.steps[0].result == pytest.approx(1.0)
    # dry mix = 1.0 * 1600 = 1600 kg ; bags = ceil(1600/25)=64
    bag_step = next(s for s in result.steps if s.label == "Bag count")
    assert bag_step.result == 64


def test_wall_mortar_default_joint_fraction():
    data = WallMortarInput(masonry_area_m2=50, wall_thickness_m=0.2)
    result = calculate_wall_mortar_v2(data)
    # volume = 50 * 0.2 * 0.2 = 2.0
    assert result.steps[0].result == pytest.approx(2.0)


def test_wall_mortar_rejects_non_positive():
    with pytest.raises(ValidationError):
        WallMortarInput(masonry_area_m2=0, wall_thickness_m=0.2)
