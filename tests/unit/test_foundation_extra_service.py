import math

import pytest
from pydantic import ValidationError

from app.schemas.foundation_extra import (
    CushionInput,
    FoundationInsulationInput,
    FoundationWaterproofingInput,
    PileInput,
)
from app.services.foundation_extra_service import (
    calculate_cushion_v2,
    calculate_foundation_insulation_v2,
    calculate_foundation_waterproofing_v2,
    calculate_pile_v2,
)


def test_pile_volumes_and_shape():
    data = PileInput(pile_count=10, pile_diameter_m=0.4, pile_length_m=6, reserve_percent=0)
    result = calculate_pile_v2(data)

    assert result.calculation_type == "foundation_pile"
    single = round(math.pi / 4 * 0.4 ** 2 * 6, 4)
    assert result.steps[0].result == pytest.approx(single)
    assert result.steps[1].result == pytest.approx(round(single * 10, 4))
    assert result.steps[3].result == 60  # total length
    assert result.materials[0].name == "Concrete"
    assert result.assumptions


def test_pile_with_rebar_estimate():
    data = PileInput(pile_count=4, pile_diameter_m=0.3, pile_length_m=5, rebar_kg_per_m3=80)
    result = calculate_pile_v2(data)
    rebar = next(m for m in result.materials if m.name.startswith("Rebar"))
    assert rebar.unit == "kg"


def test_pile_rejects_non_positive():
    with pytest.raises(ValidationError):
        PileInput(pile_count=0, pile_diameter_m=0.4, pile_length_m=6)


def test_cushion_volumes_and_geotextile():
    data = CushionInput(
        length_m=10, width_m=5, sand_thickness_m=0.1, gravel_thickness_m=0.2,
        geotextile_overlap_percent=10, waste_percent=0,
    )
    result = calculate_cushion_v2(data)

    assert result.calculation_type == "foundation_cushion"
    assert result.steps[0].result == 50  # area
    assert result.steps[1].result == pytest.approx(5.0)  # sand 50*0.1
    assert result.steps[2].result == pytest.approx(10.0)  # gravel 50*0.2
    geo = next(m for m in result.materials if m.name == "Geotextile")
    assert geo.quantity == pytest.approx(55.0)  # 50 * 1.1


def test_cushion_requires_a_thickness():
    with pytest.raises(ValidationError):
        CushionInput(length_m=10, width_m=5, sand_thickness_m=0, gravel_thickness_m=0)


def test_waterproofing_from_dimensions():
    data = FoundationWaterproofingInput(
        length_m=10, width_m=8, height_m=2, layers_count=2, overlap_percent=10, waste_percent=0
    )
    result = calculate_foundation_waterproofing_v2(data)

    # base area = 2*(10+8)*2 = 72
    assert result.steps[0].result == pytest.approx(72.0)
    # per layer = 72*1.1 = 79.2 ; total = 79.2 * 2 = 158.4
    assert result.steps[2].result == pytest.approx(158.4)


def test_waterproofing_requires_area_or_dimensions():
    with pytest.raises(ValidationError):
        FoundationWaterproofingInput(layers_count=1)


def test_waterproofing_primer_when_coverage_given():
    data = FoundationWaterproofingInput(
        surface_area_m2=100, layers_count=1, primer_coverage_m2_per_l=10
    )
    result = calculate_foundation_waterproofing_v2(data)
    primer = next(m for m in result.materials if m.name == "Primer")
    assert primer.quantity == pytest.approx(10.0)


def test_insulation_board_and_adhesive_counts():
    data = FoundationInsulationInput(
        area_m2=100, insulation_thickness_mm=50, board_length_m=1.2, board_width_m=0.6,
        adhesive_coverage_m2_per_bag=5, waste_percent=0,
    )
    result = calculate_foundation_insulation_v2(data)

    assert result.calculation_type == "foundation_insulation"
    board_step = next(s for s in result.steps if s.label == "Insulation board count")
    assert board_step.result == math.ceil(100 / (1.2 * 0.6))
    adhesive = next(m for m in result.materials if m.name == "Adhesive")
    assert adhesive.quantity == 20  # ceil(100/5)


def test_insulation_rejects_non_positive():
    with pytest.raises(ValidationError):
        FoundationInsulationInput(area_m2=0, insulation_thickness_mm=50)
    with pytest.raises(ValidationError):
        FoundationInsulationInput(area_m2=100, insulation_thickness_mm=0)
