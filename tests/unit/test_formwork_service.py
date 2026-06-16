import pytest
from pydantic import ValidationError

from app.schemas.formwork import FormworkFoundationInput
from app.services.formwork_service import calculate_formwork_foundation_v2


def test_formwork_basic_shape_and_values():
    data = FormworkFoundationInput(
        perimeter_m=36,
        height_m=0.6,
        sides_count=2,
        waste_percent=0,
    )

    result = calculate_formwork_foundation_v2(data)

    assert result.calculation_type == "formwork_foundation"
    # area = 36 * 0.6 * 2 = 43.2
    assert result.steps[0].result == 43.2
    assert result.materials[0].name == "Formwork (boards/panels)"
    assert result.materials[0].unit == "m2"
    assert result.materials[0].quantity == 43.2
    assert result.assumptions  # not empty


def test_formwork_applies_waste_reserve():
    data = FormworkFoundationInput(
        perimeter_m=36,
        height_m=0.6,
        sides_count=2,
        waste_percent=10,
    )

    result = calculate_formwork_foundation_v2(data)

    # area_with_waste = 43.2 * 1.10 = 47.52
    assert result.steps[1].result == pytest.approx(47.52)
    # waste_reserve = 47.52 - 43.2 = 4.32
    assert result.steps[2].result == pytest.approx(4.32)
    assert result.materials[0].quantity == pytest.approx(47.52)


def test_formwork_panel_count_when_panel_area_given():
    data = FormworkFoundationInput(
        perimeter_m=36,
        height_m=0.6,
        sides_count=2,
        waste_percent=0,
        panel_area_m2=2,
    )

    result = calculate_formwork_foundation_v2(data)

    # ceil(43.2 / 2) = 22
    panel_step = next(s for s in result.steps if s.label == "Panel/board count")
    assert panel_step.result == 22
    panels = next(m for m in result.materials if m.name == "Formwork panels")
    assert panels.quantity == 22
    assert panels.unit == "pcs"


def test_formwork_default_sides_count_is_two():
    data = FormworkFoundationInput(perimeter_m=10, height_m=1)
    assert data.sides_count == 2


def test_formwork_warns_on_high_waste_and_nonstandard_sides():
    data = FormworkFoundationInput(
        perimeter_m=36,
        height_m=0.6,
        sides_count=1,
        waste_percent=40,
    )

    result = calculate_formwork_foundation_v2(data)

    codes = {w.code for w in result.warnings}
    assert "high_waste_percent" in codes
    assert "non_standard_sides_count" in codes


def test_formwork_warns_on_large_height():
    data = FormworkFoundationInput(perimeter_m=36, height_m=4)

    result = calculate_formwork_foundation_v2(data)

    assert any(w.code == "large_formwork_height" for w in result.warnings)


def test_formwork_rejects_non_positive_values():
    with pytest.raises(ValidationError):
        FormworkFoundationInput(perimeter_m=0, height_m=1)
    with pytest.raises(ValidationError):
        FormworkFoundationInput(perimeter_m=10, height_m=-1)
    with pytest.raises(ValidationError):
        FormworkFoundationInput(perimeter_m=10, height_m=1, sides_count=0)


def test_formwork_rejects_negative_waste():
    with pytest.raises(ValidationError):
        FormworkFoundationInput(perimeter_m=10, height_m=1, waste_percent=-1)
