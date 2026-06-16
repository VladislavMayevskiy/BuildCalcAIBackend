from app.schemas.work_catalog import WorkFamily
from app.services import work_catalog_service


def test_all_families_have_work_types():
    work_types = work_catalog_service.list_work_types()
    families = {wt.family for wt in work_types}
    assert families == set(WorkFamily)
    assert len(work_types) == len(list(WorkFamily))


def test_get_work_type_and_missing():
    wt = work_catalog_service.get_work_type("foundations")
    assert wt is not None
    assert wt.family == WorkFamily.foundations
    assert "strip-foundation" in wt.subtype_slugs
    assert work_catalog_service.get_work_type("does-not-exist") is None


def test_subtypes_reference_calculation_templates():
    subtype = work_catalog_service.get_work_subtype("rebar-linear")
    assert subtype is not None
    assert "REBAR_LINEAR" in subtype.calculation_template_codes


def test_calculation_templates_have_endpoints():
    templates = work_catalog_service.list_calculation_templates()
    assert len(templates) >= 30
    for template in templates:
        assert template.endpoint.startswith("POST /")
        assert template.response_model == "CalculationResult"


def test_get_calculation_template_and_missing():
    template = work_catalog_service.get_calculation_template("EARTH_EXCAVATION")
    assert template is not None
    assert template.endpoint == "POST /earthworks/excavation/v2"
    assert work_catalog_service.get_calculation_template("NOPE") is None


def test_standards_lookup():
    assert work_catalog_service.get_standard("EN_1992") is not None
    assert work_catalog_service.get_standard("missing") is None


def test_method_qc_safety_for_known_subtype():
    assert work_catalog_service.get_method_statement("strip-foundation") is not None
    assert work_catalog_service.get_qc_checks("strip-foundation") is not None
    assert work_catalog_service.get_safety_rules("strip-foundation") is not None


def test_method_qc_safety_missing_returns_none():
    assert work_catalog_service.get_method_statement("unknown-subtype") is None
    assert work_catalog_service.get_qc_checks("unknown-subtype") is None
    assert work_catalog_service.get_safety_rules("unknown-subtype") is None
