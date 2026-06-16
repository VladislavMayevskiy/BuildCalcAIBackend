import pytest

from app.schemas.calculation_result import CalculationResult, MaterialItem
from app.services.estimate_service import (
    aggregate_materials,
    generate_estimate_from_calculation,
)


def _result(calc_type: str, materials: list[MaterialItem]) -> CalculationResult:
    return CalculationResult(calculation_type=calc_type, materials=materials)


def test_aggregate_sums_same_material_name_and_unit():
    results = [
        _result("strip_foundation", [MaterialItem(name="Concrete", quantity=10, unit="m3")]),
        _result("slab_foundation", [MaterialItem(name="Concrete", quantity=5.5, unit="m3")]),
    ]
    aggregated = aggregate_materials(results)

    concrete = next(m for m in aggregated.materials if m.name == "Concrete")
    assert concrete.total_quantity == pytest.approx(15.5)
    assert set(concrete.sources) == {"strip_foundation", "slab_foundation"}


def test_aggregate_keeps_different_units_separate():
    results = [
        _result("rebar_linear", [
            MaterialItem(name="Rebar", quantity=100, unit="kg"),
            MaterialItem(name="Rebar", quantity=40, unit="m"),
        ]),
    ]
    aggregated = aggregate_materials(results)
    units = {(m.name, m.unit) for m in aggregated.materials}
    assert ("Rebar", "kg") in units
    assert ("Rebar", "m") in units


def test_aggregate_does_not_invent_prices_and_warns():
    results = [_result("walls_blocks", [MaterialItem(name="Blocks", quantity=200, unit="pcs")])]
    aggregated = aggregate_materials(results)

    assert aggregated.subtotal_materials is None
    block = aggregated.materials[0]
    assert block.unit_price is None
    assert block.total_price is None
    assert any(w.code == "prices_missing" for w in aggregated.warnings)
    assert aggregated.assumptions


def test_generate_estimate_from_calculation_still_works():
    result = _result("concrete_volume", [MaterialItem(name="Concrete", quantity=3, unit="m3")])
    estimate = generate_estimate_from_calculation(result)
    assert estimate.materials[0].name == "Concrete"
    assert estimate.materials[0].unit_price is None
