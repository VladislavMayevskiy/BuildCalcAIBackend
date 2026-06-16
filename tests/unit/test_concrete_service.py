import math

import pytest
from pydantic import ValidationError

from app.schemas.concrete import ConcreteMixInput, ConcreteShape, ConcreteVolumeInput
from app.services.concrete_service import (
    calculate_concrete_mix_materials_v2,
    calculate_concrete_volume_v2,
)


def test_concrete_volume_slab():
    data = ConcreteVolumeInput(
        shape_type=ConcreteShape.slab, length_m=5, width_m=4, thickness_m=0.2, reserve_percent=0
    )
    result = calculate_concrete_volume_v2(data)
    assert result.calculation_type == "concrete_volume"
    assert result.steps[0].result == pytest.approx(4.0)  # 5*4*0.2
    assert result.materials[0].name == "Concrete"


def test_concrete_volume_cylinder_and_count():
    data = ConcreteVolumeInput(
        shape_type=ConcreteShape.cylinder, diameter_m=0.4, height_m=3, count=5, reserve_percent=0
    )
    result = calculate_concrete_volume_v2(data)
    unit = round(math.pi / 4 * 0.4 ** 2 * 3, 4)
    assert result.steps[0].result == pytest.approx(unit)
    assert result.steps[1].result == pytest.approx(round(unit * 5, 4))


def test_concrete_volume_requires_shape_dimensions():
    with pytest.raises(ValidationError):
        ConcreteVolumeInput(shape_type=ConcreteShape.slab, length_m=5, width_m=4)  # missing thickness


def test_concrete_mix_materials_shape_and_warning():
    data = ConcreteMixInput(
        concrete_volume_m3=10,
        mix_ratio_cement=1,
        mix_ratio_sand=2,
        mix_ratio_gravel=4,
    )
    result = calculate_concrete_mix_materials_v2(data)

    assert result.calculation_type == "concrete_mix_materials"
    # dry volume = 10 * 1.54 = 15.4
    assert result.steps[0].result == pytest.approx(15.4)
    names = {m.name for m in result.materials}
    assert {"Cement", "Sand", "Gravel", "Water"} <= names
    assert any(w.code == "approximate_mix_design" for w in result.warnings)
    assert result.assumptions


def test_concrete_mix_rejects_non_positive_volume():
    with pytest.raises(ValidationError):
        ConcreteMixInput(concrete_volume_m3=0, mix_ratio_cement=1, mix_ratio_sand=2, mix_ratio_gravel=4)


def test_concrete_mix_rejects_non_positive_ratio():
    with pytest.raises(ValidationError):
        ConcreteMixInput(concrete_volume_m3=10, mix_ratio_cement=0, mix_ratio_sand=2, mix_ratio_gravel=4)
