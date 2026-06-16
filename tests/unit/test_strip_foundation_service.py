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


def test_strip_foundation_input_validation_fails_for_zero_width():
    with pytest.raises(ValidationError):
        StripFoundationInput(
            length=10,
            width=0,
            foundation_width=0.4,
            foundation_depth=0.6,
            reserve_percent=10,
        )


def test_strip_foundation_input_validation_fails_for_negative_reserve():
    with pytest.raises(ValidationError):
        StripFoundationInput(
            length=10,
            width=8,
            foundation_width=0.4,
            foundation_depth=0.6,
            reserve_percent=-5,
        )


def test_strip_foundation_v2_has_expected_result_shape():
    data = StripFoundationInput(
        length=10,
        width=8,
        foundation_width=0.4,
        foundation_depth=0.6,
        reserve_percent=10,
    )

    result = calculate_strip_foundation_v2(data)

    assert result.calculation_type == "strip_foundation"
    assert len(result.steps) == 3
    assert {a.key for a in result.assumptions} >= {
        "reserve_percent",
        "perimeter_method",
        "concrete_only",
    }
    assert all(m.unit for m in result.materials)


def test_strip_foundation_v2_warns_when_no_reserve():
    data = StripFoundationInput(
        length=10,
        width=8,
        foundation_width=0.4,
        foundation_depth=0.6,
        reserve_percent=0,
    )

    result = calculate_strip_foundation_v2(data)

    assert any(w.code == "no_reserve" for w in result.warnings)


def test_strip_foundation_v2_warns_when_width_thin():
    data = StripFoundationInput(
        length=10,
        width=8,
        foundation_width=0.1,
        foundation_depth=0.6,
        reserve_percent=10,
    )

    result = calculate_strip_foundation_v2(data)

    assert any(w.code == "thin_foundation_width" for w in result.warnings)

