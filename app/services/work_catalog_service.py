"""Static construction work taxonomy catalog.

This is a plain, in-memory backend catalog (no DB, no AI, no vector search).
It exposes structured construction content: work types, subtypes, calculation
templates that point to the deterministic v2 endpoints, standards references,
and method/QC/safety guidance keyed by work subtype slug.
"""

from __future__ import annotations

from app.schemas.work_catalog import (
    CalculationTemplate,
    CostRule,
    DeliverableTemplate,
    MethodStatement,
    QCCheck,
    SafetyRule,
    StandardReference,
    WorkFamily,
    WorkSubtype,
    WorkType,
)


# (code, name, work_subtype_slug, endpoint, inputs)
_TEMPLATE_DEFS: list[tuple[str, str, str, str, list[str]]] = [
    ("EARTH_EXCAVATION", "Excavation volume", "excavation", "POST /earthworks/excavation/v2",
     ["length_m", "width_m", "depth_m", "bulking_percent"]),
    ("EARTH_TRENCH", "Trench volume", "trench", "POST /earthworks/trench/v2",
     ["trench_length_m", "trench_width_m", "trench_depth_m"]),
    ("EARTH_BACKFILL", "Backfill volume", "backfill", "POST /earthworks/backfill/v2",
     ["area_m2", "compacted_thickness_m", "compaction_factor"]),
    ("FND_STRIP", "Strip foundation", "strip-foundation", "POST /foundation/strip/v2",
     ["length", "width", "foundation_width", "foundation_depth"]),
    ("FND_SLAB", "Slab foundation", "slab-foundation", "POST /foundation/slab/v2",
     ["length", "width", "slab_thickness"]),
    ("FND_PILE", "Pile foundation", "pile-foundation", "POST /foundation/pile/v2",
     ["pile_count", "pile_diameter_m", "pile_length_m"]),
    ("FND_FORMWORK", "Foundation formwork", "formwork", "POST /foundation/formwork/v2",
     ["perimeter_m", "height_m", "sides_count"]),
    ("FND_CUSHION", "Sand/gravel cushion", "cushion", "POST /foundation/cushion/v2",
     ["length_m", "width_m", "sand_thickness_m", "gravel_thickness_m"]),
    ("FND_WATERPROOF", "Foundation waterproofing", "foundation-waterproofing", "POST /foundation/waterproofing/v2",
     ["surface_area_m2", "layers_count", "overlap_percent"]),
    ("FND_INSULATION", "Foundation insulation", "foundation-insulation", "POST /foundation/insulation/v2",
     ["area_m2", "insulation_thickness_mm"]),
    ("CONC_VOLUME", "Concrete volume by shape", "concrete-volume", "POST /concrete/volume/v2",
     ["shape_type", "dimensions", "reserve_percent"]),
    ("CONC_MIX", "Concrete mix materials", "concrete-mix", "POST /concrete/mix-materials/v2",
     ["concrete_volume_m3", "mix_ratio_cement", "mix_ratio_sand", "mix_ratio_gravel"]),
    ("REBAR_LINEAR", "Linear rebar", "rebar-linear", "POST /rebar/linear/v2",
     ["total_length_m", "bar_diameter_mm", "bar_count"]),
    ("REBAR_MESH", "Rebar mesh", "rebar-mesh", "POST /rebar/mesh/v2",
     ["area_m2", "sheet_length_m", "sheet_width_m"]),
    ("REBAR_STIRRUPS", "Rebar stirrups", "rebar-stirrups", "POST /rebar/stirrups/v2",
     ["beam_length_m", "spacing_m", "stirrup_width_m", "stirrup_height_m", "bar_diameter_mm"]),
    ("REBAR_LAP", "Rebar lap length", "rebar-lap", "POST /rebar/lap-length/v2",
     ["bar_diameter_mm", "bar_count", "lap_multiplier"]),
    ("WALL_BLOCKS", "Block walls", "wall-blocks", "POST /walls/blocks/v2",
     ["wall_length_m", "wall_height_m", "block_length_m", "block_height_m"]),
    ("WALL_BRICKS", "Brick walls", "wall-bricks", "POST /walls/bricks/v2",
     ["wall_length_m", "wall_height_m", "brick_length_m", "brick_height_m"]),
    ("WALL_MORTAR", "Masonry mortar", "wall-mortar", "POST /walls/mortar/v2",
     ["masonry_area_m2", "wall_thickness_m"]),
    ("FACADE_AREA", "Facade area", "facade-area", "POST /facade/area/v2",
     ["facades", "openings_area_m2"]),
    ("FACADE_INSULATION", "Facade insulation", "facade-insulation", "POST /facade/insulation/v2",
     ["area_m2", "board_length_m", "board_width_m"]),
    ("FACADE_PLASTER", "Facade plaster", "facade-plaster", "POST /facade/plaster/v2",
     ["area_m2", "plaster_kg_per_m2"]),
    ("FACADE_PAINT", "Facade paint", "facade-paint", "POST /facade/paint/v2",
     ["area_m2", "paint_coverage_m2_per_l", "coats_count"]),
    ("FLOOR_SCREED", "Floor screed", "floor-screed", "POST /floors/screed/v2",
     ["area_m2", "thickness_m"]),
    ("FLOOR_INSULATION", "Floor insulation", "floor-insulation", "POST /floors/insulation/v2",
     ["area_m2", "thickness_mm"]),
    ("FLOOR_LAMINATE", "Laminate flooring", "floor-laminate", "POST /floors/laminate/v2",
     ["area_m2", "pack_area_m2", "perimeter_m"]),
    ("TILES_FLOOR", "Floor tiles", "tiles-floor", "POST /tiles/floor/v2",
     ["area_m2", "tile_length_m", "tile_width_m"]),
    ("TILES_WALL", "Wall tiles", "tiles-wall", "POST /tiles/wall/v2",
     ["gross_area_m2", "openings_area_m2", "tile_length_m", "tile_width_m"]),
    ("TILES_ADHESIVE", "Tile adhesive", "tiles-adhesive", "POST /tiles/adhesive/v2",
     ["area_m2", "adhesive_kg_per_m2", "bag_weight_kg"]),
    ("TILES_GROUT", "Tile grout", "tiles-grout", "POST /tiles/grout/v2",
     ["area_m2", "grout_kg_per_m2"]),
    ("ROOF_AREA", "Roof area", "roof-area", "POST /roof/area/v2",
     ["length_m", "width_m", "slope_degrees"]),
    ("ROOF_COVERING", "Roof covering", "roof-covering", "POST /roof/covering/v2",
     ["roof_area_m2", "sheet_length_m", "sheet_width_m"]),
    ("ROOF_MEMBRANE", "Roof membrane", "roof-membrane", "POST /roof/membrane/v2",
     ["roof_area_m2", "roll_area_m2"]),
    ("ROOF_INSULATION", "Roof insulation", "roof-insulation", "POST /roof/insulation/v2",
     ["roof_area_m2", "thickness_mm"]),
    ("ROOF_GUTTERS", "Roof gutters", "roof-gutters", "POST /roof/gutters/v2",
     ["eaves_length_m", "downpipe_spacing_m"]),
    ("MEP_HEAT_LOSS", "HVAC basic heat loss", "hvac-heat-loss", "POST /mep/hvac/heat-loss-basic/v2",
     ["surfaces", "delta_t_k"]),
    ("MEP_ELEC_LOAD", "Electrical basic load", "electrical-load", "POST /mep/electrical/load-basic/v2",
     ["loads", "voltage_v", "phase_type"]),
    ("MEP_PIPE_VOLUME", "Plumbing pipe volume", "plumbing-pipe-volume", "POST /mep/plumbing/pipe-volume/v2",
     ["pipe_runs"]),
]

# work_subtype_slug -> (display name, family)
_SUBTYPE_META: dict[str, tuple[str, WorkFamily]] = {
    "excavation": ("Excavation", WorkFamily.earthworks),
    "trench": ("Trench", WorkFamily.earthworks),
    "backfill": ("Backfill", WorkFamily.earthworks),
    "strip-foundation": ("Strip foundation", WorkFamily.foundations),
    "slab-foundation": ("Slab foundation", WorkFamily.foundations),
    "pile-foundation": ("Pile foundation", WorkFamily.foundations),
    "formwork": ("Formwork", WorkFamily.foundations),
    "cushion": ("Sand/gravel cushion", WorkFamily.foundations),
    "foundation-waterproofing": ("Foundation waterproofing", WorkFamily.foundations),
    "foundation-insulation": ("Foundation insulation", WorkFamily.foundations),
    "concrete-volume": ("Concrete volume", WorkFamily.concrete),
    "concrete-mix": ("Concrete mix", WorkFamily.concrete),
    "rebar-linear": ("Linear rebar", WorkFamily.rebar),
    "rebar-mesh": ("Rebar mesh", WorkFamily.rebar),
    "rebar-stirrups": ("Rebar stirrups", WorkFamily.rebar),
    "rebar-lap": ("Rebar lap length", WorkFamily.rebar),
    "wall-blocks": ("Block walls", WorkFamily.walls_masonry),
    "wall-bricks": ("Brick walls", WorkFamily.walls_masonry),
    "wall-mortar": ("Masonry mortar", WorkFamily.walls_masonry),
    "facade-area": ("Facade area", WorkFamily.facade),
    "facade-insulation": ("Facade insulation", WorkFamily.facade),
    "facade-plaster": ("Facade plaster", WorkFamily.facade),
    "facade-paint": ("Facade paint", WorkFamily.facade),
    "floor-screed": ("Floor screed", WorkFamily.floors),
    "floor-insulation": ("Floor insulation", WorkFamily.floors),
    "floor-laminate": ("Laminate flooring", WorkFamily.floors),
    "tiles-floor": ("Floor tiles", WorkFamily.tiles),
    "tiles-wall": ("Wall tiles", WorkFamily.tiles),
    "tiles-adhesive": ("Tile adhesive", WorkFamily.tiles),
    "tiles-grout": ("Tile grout", WorkFamily.tiles),
    "roof-area": ("Roof area", WorkFamily.roofing),
    "roof-covering": ("Roof covering", WorkFamily.roofing),
    "roof-membrane": ("Roof membrane", WorkFamily.roofing),
    "roof-insulation": ("Roof insulation", WorkFamily.roofing),
    "roof-gutters": ("Roof gutters", WorkFamily.roofing),
    "hvac-heat-loss": ("HVAC heat loss (basic)", WorkFamily.mep),
    "electrical-load": ("Electrical load (basic)", WorkFamily.mep),
    "plumbing-pipe-volume": ("Plumbing pipe volume", WorkFamily.mep),
}

# One work type per family; families without dedicated subtypes are still listed.
_FAMILY_WORK_TYPE_NAMES: dict[WorkFamily, str] = {
    WorkFamily.site_preparation: "Site preparation",
    WorkFamily.earthworks: "Earthworks",
    WorkFamily.foundations: "Foundations",
    WorkFamily.concrete: "Concrete",
    WorkFamily.rebar: "Reinforcement (rebar)",
    WorkFamily.structural_frame: "Structural frame",
    WorkFamily.walls_masonry: "Walls and masonry",
    WorkFamily.facade: "Facade",
    WorkFamily.roofing: "Roofing",
    WorkFamily.floors: "Floors",
    WorkFamily.tiles: "Tiles",
    WorkFamily.interior_finishing: "Interior finishing",
    WorkFamily.mep: "MEP (mechanical, electrical, plumbing)",
    WorkFamily.drainage: "Drainage",
    WorkFamily.landscaping: "Landscaping",
    WorkFamily.demolition: "Demolition",
    WorkFamily.reconstruction: "Reconstruction",
    WorkFamily.special_works: "Special works",
}


def _build_catalog():
    templates: list[CalculationTemplate] = []
    subtypes: dict[str, WorkSubtype] = {}

    for slug, (name, family) in _SUBTYPE_META.items():
        subtypes[slug] = WorkSubtype(
            slug=slug,
            name=name,
            work_type_slug=family.value,
            family=family,
            description=f"{name} work subtype in the {family.value} family.",
            calculation_template_codes=[],
        )

    for code, name, subtype_slug, endpoint, inputs in _TEMPLATE_DEFS:
        templates.append(
            CalculationTemplate(
                code=code,
                name=name,
                work_subtype_slug=subtype_slug,
                endpoint=endpoint,
                inputs=inputs,
            )
        )
        if subtype_slug in subtypes:
            subtypes[subtype_slug].calculation_template_codes.append(code)

    work_types: dict[str, WorkType] = {}
    for family, type_name in _FAMILY_WORK_TYPE_NAMES.items():
        work_types[family.value] = WorkType(
            slug=family.value,
            name=type_name,
            family=family,
            description=f"{type_name} construction work family.",
            subtype_slugs=[s.slug for s in subtypes.values() if s.family == family],
        )

    return work_types, subtypes, templates


_WORK_TYPES, _WORK_SUBTYPES, _CALCULATION_TEMPLATES = _build_catalog()

_STANDARDS: dict[str, StandardReference] = {
    "DBN_V22": StandardReference(
        code="DBN_V22", title="DBN V.2.2 series (buildings and structures)", region="UA",
        scope="General building design requirements.",
    ),
    "DBN_FOUNDATIONS": StandardReference(
        code="DBN_FOUNDATIONS", title="DBN foundations and soil bases", region="UA",
        scope="Foundations, soil bases, earthworks.",
    ),
    "DSTU_CONCRETE": StandardReference(
        code="DSTU_CONCRETE", title="DSTU concrete and reinforced concrete", region="UA",
        scope="Concrete classes, mixes and reinforcement.",
    ),
    "EN_1992": StandardReference(
        code="EN_1992", title="Eurocode 2: Design of concrete structures", region="EU",
        scope="Reference for reinforcement, lap lengths, concrete design.",
    ),
}

_METHOD_STATEMENTS: dict[str, MethodStatement] = {
    "excavation": MethodStatement(work_subtype_slug="excavation", steps=[
        "Set out the excavation footprint and reference levels.",
        "Strip topsoil and stockpile separately.",
        "Excavate to design depth, battering or shoring as required.",
        "Trim and level the formation, protect against water ingress.",
    ]),
    "strip-foundation": MethodStatement(work_subtype_slug="strip-foundation", steps=[
        "Excavate the trench to design width and depth.",
        "Place and compact the cushion if specified.",
        "Install formwork and reinforcement.",
        "Pour and cure the concrete.",
    ]),
    "tiles-floor": MethodStatement(work_subtype_slug="tiles-floor", steps=[
        "Prepare and prime the substrate.",
        "Set out tiles from the room centre or focal line.",
        "Apply adhesive and lay tiles with spacers.",
        "Grout joints after the adhesive has cured.",
    ]),
}

_QC_CHECKS: dict[str, QCCheck] = {
    "excavation": QCCheck(work_subtype_slug="excavation", checks=[
        "Verify excavation dimensions and levels against drawings.",
        "Confirm formation bearing capacity / inspection sign-off.",
        "Check side stability and dewatering.",
    ]),
    "strip-foundation": QCCheck(work_subtype_slug="strip-foundation", checks=[
        "Check reinforcement size, spacing and cover.",
        "Verify concrete class and slump on delivery.",
        "Confirm dimensions and alignment of formwork.",
    ]),
    "tiles-floor": QCCheck(work_subtype_slug="tiles-floor", checks=[
        "Check flatness and adhesive coverage (no voids).",
        "Verify joint width consistency and alignment.",
        "Confirm grout is fully tooled and cleaned.",
    ]),
}

_SAFETY_RULES: dict[str, SafetyRule] = {
    "excavation": SafetyRule(work_subtype_slug="excavation", rules=[
        "Provide shoring or battering for deep excavations.",
        "Keep spoil and plant clear of excavation edges.",
        "Check for buried services before digging.",
    ]),
    "strip-foundation": SafetyRule(work_subtype_slug="strip-foundation", rules=[
        "Use PPE when handling reinforcement and concrete.",
        "Protect rebar starter bars (cap exposed ends).",
        "Ensure safe access into and out of trenches.",
    ]),
    "tiles-floor": SafetyRule(work_subtype_slug="tiles-floor", rules=[
        "Use eye protection when cutting tiles.",
        "Control silica dust during cutting (water/extraction).",
        "Keep walkways clear of adhesive and offcuts.",
    ]),
}

_DELIVERABLE_TEMPLATES: dict[str, DeliverableTemplate] = {
    "QUANTITY_SHEET": DeliverableTemplate(code="QUANTITY_SHEET", name="Quantity take-off sheet", items=[
        "Material list with quantities and units",
        "Assumptions and warnings",
        "Calculation steps",
    ]),
}

_COST_RULES: dict[str, CostRule] = {
    "WASTE_RESERVE": CostRule(code="WASTE_RESERVE", name="Apply waste reserve",
                              description="Quantities should include a waste/reserve percentage before pricing."),
    "NO_INVENTED_PRICES": CostRule(code="NO_INVENTED_PRICES", name="No invented prices",
                                   description="Prices must come from stored catalog data; never invent exact prices."),
}


def list_work_types() -> list[WorkType]:
    return list(_WORK_TYPES.values())


def get_work_type(slug: str) -> WorkType | None:
    return _WORK_TYPES.get(slug)


def list_work_subtypes() -> list[WorkSubtype]:
    return list(_WORK_SUBTYPES.values())


def get_work_subtype(slug: str) -> WorkSubtype | None:
    return _WORK_SUBTYPES.get(slug)


def list_calculation_templates() -> list[CalculationTemplate]:
    return list(_CALCULATION_TEMPLATES)


def get_calculation_template(code: str) -> CalculationTemplate | None:
    for template in _CALCULATION_TEMPLATES:
        if template.code == code:
            return template
    return None


def list_standards() -> list[StandardReference]:
    return list(_STANDARDS.values())


def get_standard(code: str) -> StandardReference | None:
    return _STANDARDS.get(code)


def get_method_statement(work_subtype_slug: str) -> MethodStatement | None:
    return _METHOD_STATEMENTS.get(work_subtype_slug)


def get_qc_checks(work_subtype_slug: str) -> QCCheck | None:
    return _QC_CHECKS.get(work_subtype_slug)


def get_safety_rules(work_subtype_slug: str) -> SafetyRule | None:
    return _SAFETY_RULES.get(work_subtype_slug)


def list_deliverable_templates() -> list[DeliverableTemplate]:
    return list(_DELIVERABLE_TEMPLATES.values())


def list_cost_rules() -> list[CostRule]:
    return list(_COST_RULES.values())
