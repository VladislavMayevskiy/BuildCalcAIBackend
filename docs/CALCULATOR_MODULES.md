# Calculator Modules

This document describes the calculator modules for the "House from 0 to 100" scope.

> Implemented deterministic calculators live in `app/services/` with schemas in `app/schemas/` and routes in `app/api/routes/`. The folders under `app/domain/` remain placeholders (no migration yet).

## Standard contract

Every v2 calculator returns a `CalculationResult` with `calculation_type`, `steps`, `materials`, `assumptions`, and `warnings`. Formulas live only in services; routes handle auth/validation/persistence. No AI/OpenAI is used in any calculator.

## Implemented modules and calculators

- **earthworks** (`earthworks_service`): excavation, trench, backfill
- **foundation** (`strip_foundation_service`, `slab_foundation_service`, `formwork_service`, `foundation_extra_service`): strip v1/v2, slab v2, formwork v2, pile v2, cushion v2, waterproofing v2, insulation v2
- **concrete** (`concrete_service`): volume by shape (prism/slab/column/beam/cylinder), approximate mix materials
- **rebar** (`rebar_service`): linear, mesh, stirrups, lap-length (uses nominal mass `diameter_mm² / 162`)
- **walls** (`walls_service`): blocks, bricks, mortar (openings subtraction, joint thickness)
- **facade** (`facade_service`): area, insulation, plaster, paint
- **floors** (`floors_service`): screed, insulation, laminate
- **tiles** (`tiles_service`): floor, wall, adhesive, grout
- **roofing** (`roofing_service`): area (slope factor), covering, membrane, insulation, gutters
- **mep** (`mep_service`): basic HVAC heat loss, basic electrical load, plumbing pipe volume (preliminary, with warnings)
- **room** (`calculation_service`): room calculation v1/v2

## Supporting modules

- **estimates** (`estimate_service`): basic estimate from a stored v2 `CalculationResult`; deterministic material aggregation across multiple results (grouped by name + unit, source `calculation_type` preserved, no invented prices)
- **work catalog** (`work_catalog_service`): static taxonomy — work types, subtypes, calculation templates (pointing at the v2 endpoints), standards, method statements, QC checks, safety rules. Plain backend catalog: no AI, no vector search, no DB.
- **materials / projects**: skeletal models only; full catalog with real prices and project-level workflow remain planned

## Planned (not implemented)

- standalone `insulation`/`waterproofing` module endpoints (currently embedded in foundation/facade/floors/roof)
- interior `finishing` calculators (putty/primer/wallpaper/drywall)
- material catalog with real prices and estimate pricing
- project-level workflow and stage aggregation
