import pytest

from app.schemas.calculation import CalculationInput
from app.services.calculation_service import calculate_room_v2


def test_calculate_room_v2_returns_correct_structure():
    data = CalculationInput(
        length=5,
        width=4,
        height=2.7,
        windows_area=2,
        doors_area=2.6,
    )

    result = calculate_room_v2(data)

    assert result.calculation_type == "room_calculation"

    assert len(result.steps) == 9
    assert len(result.materials) == 2
    assert len(result.assumptions) == 3
    assert result.warnings == []


def test_calculate_room_v2_calculates_correct_values():
    data = CalculationInput(
        length=5,
        width=4,
        height=2.7,
        windows_area=2,
        doors_area=2.6,
    )

    result = calculate_room_v2(data)

    steps_by_label = {step.label: step for step in result.steps}

    assert steps_by_label["Floor area"].result == 20
    assert steps_by_label["Ceiling area"].result == 20
    assert steps_by_label["Room perimeter"].result == 18
    assert steps_by_label["Wall area before openings"].result == 48.6
    assert steps_by_label["Openings area"].result == 4.6
    assert steps_by_label["Net wall area"].result == 44
    assert steps_by_label["Wall area with reserve"].result == 48.4
    assert steps_by_label["Paint required"].result == 5.38
    assert steps_by_label["Floor tile required"].result == 22


def test_calculate_room_v2_returns_materials():
    data = CalculationInput(
        length=5,
        width=4,
        height=2.7,
        windows_area=2,
        doors_area=2.6,
    )

    result = calculate_room_v2(data)

    materials_by_name = {material.name: material for material in result.materials}

    assert "Paint" in materials_by_name
    assert "Floor tiles" in materials_by_name

    assert materials_by_name["Paint"].quantity == 5.38
    assert materials_by_name["Paint"].unit == "liters"

    assert materials_by_name["Floor tiles"].quantity == 22
    assert materials_by_name["Floor tiles"].unit == "m2"
    assert materials_by_name["Floor tiles"].waste_percent == 10


def test_calculate_room_v2_returns_assumptions():
    data = CalculationInput(
        length=5,
        width=4,
        height=2.7,
        windows_area=2,
        doors_area=2.6,
    )

    result = calculate_room_v2(data)

    assumption_keys = {assumption.key for assumption in result.assumptions}

    assert "wall_reserve" in assumption_keys
    assert "paint_coverage" in assumption_keys
    assert "tile_reserve" in assumption_keys


def test_calculate_room_v2_raises_error_when_openings_exceed_wall_area():
    data = CalculationInput(
        length=2,
        width=2,
        height=2,
        windows_area=100,
        doors_area=100,
    )

    with pytest.raises(ValueError, match="Windows and doors area cannot exceed total wall area"):
        calculate_room_v2(data)


def test_calculate_room_v2_returns_warning_when_openings_are_too_large():
    data = CalculationInput(
        length=5,
        width=4,
        height=2.7,
        windows_area=20,
        doors_area=15,
    )

    result = calculate_room_v2(data)

    assert len(result.warnings) == 1
    assert result.warnings[0].code == "large_openings_area"
    assert result.warnings[0].severity == "warning"

