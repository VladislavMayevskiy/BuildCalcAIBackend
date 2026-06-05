# Calculator Modules (Roadmap)

This document describes the **planned** calculator modules for the long-term "House from 0 to 100" scope.

> Important: these modules are **not implemented** yet. The corresponding folders under `app/domain/` are placeholders only.

## Modules

- **earthworks**: excavation, trenching, backfill, compaction volumes
- **foundation**: strip/slab/pile foundations, formwork, waterproofing, insulation, rebar (foundation scope)
- **concrete**: concrete volumes and concrete-related materials
- **rebar**: rebar length/weight/meshes/laps/stirrups
- **walls**: masonry/block/brick quantities, openings subtraction, mortar/glue estimates
- **facade**: facade area, insulation systems, plaster/paint
- **roofing**: roof geometry, coverings, membranes, insulation (roof scope)
- **insulation**: insulation quantities for facade/roof/floors (module-level)
- **waterproofing**: membranes, overlaps, area-based waterproofing (module-level)
- **finishing**: plaster/putty/primer/paint and other interior finishing calculators
- **tiles**: wall/floor tiles, adhesive, grout
- **floors**: screed, laminate/parquet/vinyl, baseboards
- **materials**: material catalog, units, normalization, future price integration
- **estimates**: aggregations of calculator outputs into estimate line items
- **projects**: project-level workflow and stage aggregation

## Current implemented calculators

Working calculators currently live in `app/services/`:

- room calculation v1/v2
- strip foundation v1/v2

