from enum import Enum

from pydantic import BaseModel, Field


class WorkFamily(str, Enum):
    site_preparation = "site_preparation"
    earthworks = "earthworks"
    foundations = "foundations"
    concrete = "concrete"
    rebar = "rebar"
    structural_frame = "structural_frame"
    walls_masonry = "walls_masonry"
    facade = "facade"
    roofing = "roofing"
    floors = "floors"
    tiles = "tiles"
    interior_finishing = "interior_finishing"
    mep = "mep"
    drainage = "drainage"
    landscaping = "landscaping"
    demolition = "demolition"
    reconstruction = "reconstruction"
    special_works = "special_works"


class WorkType(BaseModel):
    slug: str
    name: str
    family: WorkFamily
    description: str = ""
    subtype_slugs: list[str] = Field(default_factory=list)


class WorkSubtype(BaseModel):
    slug: str
    name: str
    work_type_slug: str
    family: WorkFamily
    description: str = ""
    calculation_template_codes: list[str] = Field(default_factory=list)


class CalculationTemplate(BaseModel):
    code: str
    name: str
    work_subtype_slug: str
    endpoint: str
    response_model: str = "CalculationResult"
    inputs: list[str] = Field(default_factory=list)


class StandardReference(BaseModel):
    code: str
    title: str
    region: str = ""
    scope: str = ""


class MethodStatement(BaseModel):
    work_subtype_slug: str
    steps: list[str] = Field(default_factory=list)


class QCCheck(BaseModel):
    work_subtype_slug: str
    checks: list[str] = Field(default_factory=list)


class SafetyRule(BaseModel):
    work_subtype_slug: str
    rules: list[str] = Field(default_factory=list)


class DeliverableTemplate(BaseModel):
    code: str
    name: str
    items: list[str] = Field(default_factory=list)


class CostRule(BaseModel):
    code: str
    name: str
    description: str = ""
