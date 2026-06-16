from fastapi import APIRouter, HTTPException, status

from app.schemas.work_catalog import (
    CalculationTemplate,
    MethodStatement,
    QCCheck,
    SafetyRule,
    StandardReference,
    WorkSubtype,
    WorkType,
)
from app.services import work_catalog_service

router = APIRouter(tags=["Work Catalog"])


@router.get("/work-types", response_model=list[WorkType])
def get_work_types():
    return work_catalog_service.list_work_types()


@router.get("/work-types/{slug}", response_model=WorkType)
def get_work_type(slug: str):
    work_type = work_catalog_service.get_work_type(slug)
    if work_type is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Work type not found")
    return work_type


@router.get("/work-subtypes", response_model=list[WorkSubtype])
def get_work_subtypes():
    return work_catalog_service.list_work_subtypes()


@router.get("/work-subtypes/{slug}", response_model=WorkSubtype)
def get_work_subtype(slug: str):
    subtype = work_catalog_service.get_work_subtype(slug)
    if subtype is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Work subtype not found")
    return subtype


@router.get("/calculation-templates", response_model=list[CalculationTemplate])
def get_calculation_templates():
    return work_catalog_service.list_calculation_templates()


@router.get("/calculation-templates/{code}", response_model=CalculationTemplate)
def get_calculation_template(code: str):
    template = work_catalog_service.get_calculation_template(code)
    if template is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Calculation template not found")
    return template


@router.get("/standards", response_model=list[StandardReference])
def get_standards():
    return work_catalog_service.list_standards()


@router.get("/standards/{code}", response_model=StandardReference)
def get_standard(code: str):
    standard = work_catalog_service.get_standard(code)
    if standard is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Standard not found")
    return standard


@router.get("/method-statements/{work_subtype_slug}", response_model=MethodStatement)
def get_method_statement(work_subtype_slug: str):
    statement = work_catalog_service.get_method_statement(work_subtype_slug)
    if statement is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Method statement not found")
    return statement


@router.get("/qc-checks/{work_subtype_slug}", response_model=QCCheck)
def get_qc_checks(work_subtype_slug: str):
    checks = work_catalog_service.get_qc_checks(work_subtype_slug)
    if checks is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="QC checks not found")
    return checks


@router.get("/safety-rules/{work_subtype_slug}", response_model=SafetyRule)
def get_safety_rules(work_subtype_slug: str):
    rules = work_catalog_service.get_safety_rules(work_subtype_slug)
    if rules is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Safety rules not found")
    return rules
