import pytest

from app.schemas.slab_foundation import SlabFoundationInput
from app.services.slab_foundation_service import calculate_slab_foundation_v2
from pydantic import ValidationError


def test_calculate_slab_foundation_v2_returns_expected_values():
    data = SlabFoundationInput(
        length=12,
        width=10,
        slab_thickness=0.15,
        reserve_percent=10,
    )

    result = calculate_slab_foundation_v2(data)

    assert result.calculation_type == "slab_foundation"
    assert result.steps[0].label == "Slab area"
    assert result.materials[0].name == "Concrete"
    assert result.materials[0].quantity == 19.8
    assert result.warnings == []


def test_calculate_slab_foundation_v2_warns_when_thickness_large():
    data = SlabFoundationInput(
        length=4,
        width=4,
        slab_thickness=2,
        reserve_percent=10,
    )

    result = calculate_slab_foundation_v2(data)

    assert any(w.code == "thickness_too_large" for w in result.warnings)


def test_slab_foundation_input_validation_fails_for_zero_thickness():
    with pytest.raises(ValidationError):
        SlabFoundationInput(
            length=10,
            width=8,
            slab_thickness=0,
            reserve_percent=10,
        )
