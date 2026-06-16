import pytest
from pydantic import ValidationError

from app.schemas.earthworks import BackfillInput, ExcavationInput, TrenchInput
from app.services.earthworks_service import (
    calculate_backfill_v2,
    calculate_excavation_v2,
    calculate_trench_v2,
)


def test_excavation_basic_values_and_shape():
    data = ExcavationInput(length_m=10, width_m=5, depth_m=2)
    result = calculate_excavation_v2(data)

    assert result.calculation_type == "earthworks_excavation"
    assert result.steps[0].result == 100  # 10*5*2
    assert result.materials
    assert result.assumptions
    # no extra options -> volumes equal base
    assert result.steps[1].result == 100


def test_excavation_with_bulking_and_backfill():
    data = ExcavationInput(
        length_m=10, width_m=5, depth_m=2, bulking_percent=25, backfill_percent=30, waste_percent=0
    )
    result = calculate_excavation_v2(data)

    assert result.steps[2].result == pytest.approx(125.0)  # 100 * 1.25
    backfill = next(m for m in result.materials if m.name.startswith("Backfill"))
    assert backfill.quantity == pytest.approx(30.0)


def test_excavation_warns_on_deep():
    data = ExcavationInput(length_m=10, width_m=5, depth_m=5)
    result = calculate_excavation_v2(data)
    assert any(w.code == "deep_excavation" for w in result.warnings)


def test_excavation_rejects_non_positive():
    with pytest.raises(ValidationError):
        ExcavationInput(length_m=0, width_m=5, depth_m=2)
    with pytest.raises(ValidationError):
        ExcavationInput(length_m=10, width_m=5, depth_m=-2)


def test_trench_volumes_and_remaining():
    data = TrenchInput(
        trench_length_m=20,
        trench_width_m=0.6,
        trench_depth_m=1.2,
        bedding_thickness_m=0.1,
        pipe_zone_height_m=0.3,
    )
    result = calculate_trench_v2(data)

    assert result.calculation_type == "earthworks_trench"
    # trench vol = 20*0.6*1.2 = 14.4
    assert result.steps[0].result == pytest.approx(14.4)
    # bedding = 20*0.6*0.1 = 1.2
    assert result.steps[2].result == pytest.approx(1.2)
    # remaining = 14.4 - 1.2 - (20*0.6*0.3=3.6) = 9.6
    assert result.steps[4].result == pytest.approx(9.6)


def test_trench_warns_when_zones_exceed_depth():
    data = TrenchInput(
        trench_length_m=10,
        trench_width_m=0.5,
        trench_depth_m=0.5,
        bedding_thickness_m=0.4,
        pipe_zone_height_m=0.4,
    )
    result = calculate_trench_v2(data)
    assert any(w.code == "zones_exceed_depth" for w in result.warnings)
    remaining = next(s for s in result.steps if s.label == "Remaining backfill volume")
    assert remaining.result == 0


def test_trench_rejects_non_positive():
    with pytest.raises(ValidationError):
        TrenchInput(trench_length_m=-1, trench_width_m=0.5, trench_depth_m=1)


def test_backfill_volumes_and_layers():
    data = BackfillInput(
        area_m2=50,
        compacted_thickness_m=0.3,
        compaction_factor=1.2,
        layer_thickness_m=0.15,
        waste_percent=10,
    )
    result = calculate_backfill_v2(data)

    assert result.calculation_type == "earthworks_backfill"
    # compacted = 50*0.3 = 15
    assert result.steps[0].result == pytest.approx(15.0)
    # loose = 15*1.2 = 18
    assert result.steps[1].result == pytest.approx(18.0)
    # with waste = 18*1.1 = 19.8
    assert result.steps[2].result == pytest.approx(19.8)
    layer_step = next(s for s in result.steps if s.label == "Layer count")
    assert layer_step.result == 2  # ceil(0.3/0.15)


def test_backfill_rejects_non_positive():
    with pytest.raises(ValidationError):
        BackfillInput(area_m2=0, compacted_thickness_m=0.3)
    with pytest.raises(ValidationError):
        BackfillInput(area_m2=50, compacted_thickness_m=0)
