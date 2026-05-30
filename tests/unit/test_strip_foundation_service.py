import pytest

from app.schemas.strip_foundation import StripFoundationInput
from app.services.strip_foundation_service import calculate_strip_foundation
from app.services.strip_foundation_service import calculate_strip_foundation_v2
from pydantic import ValidationError


def test_calculate_strip_foundation_returns_correct_values():
    data = StripFoundationInput(
        length=10,
        width=8,
        foundation_width=0.4,
        foundation_depth=0.6,
        reserve_percent=10,
    )

    result = calculate_strip_foundation(data)

    assert result.perimeter == 36
    assert result.concrete_volume == 8.64
    assert result.concrete_volume_with_reserve == 9.5


def test_calculate_strip_foundation_with_zero_reserve():
    data = StripFoundationInput(
        length=10,
        width=8,
        foundation_width=0.4,
        foundation_depth=0.6,
        reserve_percent=0,
    )

    result = calculate_strip_foundation(data)

    assert result.perimeter == 36
    assert result.concrete_volume == 8.64
    assert result.concrete_volume_with_reserve == 8.64


def test_calculate_strip_foundation_v2_includes_material_and_assumption():
    data = StripFoundationInput(
        length=10,
        width=8,
        foundation_width=0.4,
        foundation_depth=0.6,
        reserve_percent=10,
    )

    result = calculate_strip_foundation_v2(data)

    assert result.calculation_type == "strip_foundation"
    assert result.materials[0].name == "Concrete"
    assert result.materials[0].unit == "m3"
    assert result.assumptions[0].key == "reserve_percent"
    assert result.warnings == []


def test_calculate_strip_foundation_v2_warns_when_reserve_too_high():
    data = StripFoundationInput(
        length=10,
        width=8,
        foundation_width=0.4,
        foundation_depth=0.6,
        reserve_percent=40,
    )

    result = calculate_strip_foundation_v2(data)

    assert any(w.code == "high_reserve_percent" for w in result.warnings)


def test_strip_foundation_input_validation_fails_for_negative_dimensions():
    with pytest.raises(ValidationError):
        StripFoundationInput(
            length=-10,
            width=8,
            foundation_width=0.4,
            foundation_depth=0.6,
            reserve_percent=10,
        )

