# BuildCalcAi API Endpoints

## Implemented endpoints (current)

### Health

- `GET /` — API status message

### Auth

- `POST /login` — OAuth2 password login, returns JWT bearer token

### Users

- `POST /users/` — create user

### Rooms

- `POST /rooms/` — create room
- `GET /rooms/` — list rooms
- `GET /rooms/{room_id}` — get room
- `PATCH /rooms/{room_id}` — update room
- `DELETE /rooms/{room_id}` — delete room
- `POST /rooms/{room_id}/calculate` — calculate saved room (v1 result shape)
- `GET /rooms/{room_id}/calculations` — room calculation history

### Calculations

- `GET /calculations/history` — user calculation history
- `POST /calculate` — room calculation v1
- `POST /calculate/v2` — room calculation v2

### Earthworks (v2, returns `CalculationResult`)

- `POST /earthworks/excavation/v2` — excavation volume, bulking, soil removal, optional backfill
- `POST /earthworks/trench/v2` — trench volume, bedding, pipe-zone and remaining backfill
- `POST /earthworks/backfill/v2` — compacted/loose volume, layers, material quantity

### Foundation (v2 calculators return `CalculationResult`)

- `POST /foundation/strip` — strip foundation v1
- `POST /foundation/strip/v2` — strip foundation v2
- `POST /foundation/slab/v2` — slab foundation v2
- `POST /foundation/formwork/v2` — formwork area, panel count, waste reserve
- `POST /foundation/pile/v2` — pile concrete volume, total length, optional rebar estimate
- `POST /foundation/cushion/v2` — sand/gravel cushion volume, optional geotextile area
- `POST /foundation/waterproofing/v2` — membrane area with overlap/waste, optional primer
- `POST /foundation/insulation/v2` — insulation area/volume, board count, optional adhesive

### Concrete (v2, returns `CalculationResult`)

- `POST /concrete/volume/v2` — concrete volume by shape (prism, slab, column, beam, cylinder)
- `POST /concrete/mix-materials/v2` — approximate cement/sand/gravel/water mix quantities

### Rebar (v2, returns `CalculationResult`)

- `POST /rebar/linear/v2` — linear rebar length, lap, weight by diameter
- `POST /rebar/mesh/v2` — mesh sheets, overlap, optional weight estimate
- `POST /rebar/stirrups/v2` — stirrup count, length per stirrup, total weight
- `POST /rebar/lap-length/v2` — lap length and total overlap length
- `POST /rebar/calculation` — legacy bars calculation (v1 response shape)

### Walls / Masonry (v2, returns `CalculationResult`)

- `POST /walls/blocks/v2` — block count, net area, optional glue/mortar
- `POST /walls/bricks/v2` — brick count, net area, optional mortar volume
- `POST /walls/mortar/v2` — mortar volume, dry mix, optional bags

### Facade (v2, returns `CalculationResult`)

- `POST /facade/area/v2` — gross/net facade area with waste
- `POST /facade/insulation/v2` — board count, adhesive, dowels, mesh
- `POST /facade/plaster/v2` — plaster quantity, optional primer
- `POST /facade/paint/v2` — paint liters by coats, optional primer

### Floors (v2, returns `CalculationResult`)

- `POST /floors/screed/v2` — screed volume, dry mix, optional bags
- `POST /floors/insulation/v2` — insulation area/volume, optional board count
- `POST /floors/laminate/v2` — laminate area, packs, underlay, baseboard

### Tiles (v2, returns `CalculationResult`)

- `POST /tiles/floor/v2` — floor tile count, adhesive, grout, packs
- `POST /tiles/wall/v2` — wall tiles with openings subtraction
- `POST /tiles/adhesive/v2` — adhesive kg and bag count
- `POST /tiles/grout/v2` — approximate grout kg, optional bags

### Roofing (v2, returns `CalculationResult`)

- `POST /roof/area/v2` — plan/sloped roof area with waste
- `POST /roof/covering/v2` — covering area, sheet/tile count, fasteners
- `POST /roof/membrane/v2` — membrane area, roll count, overlap
- `POST /roof/insulation/v2` — insulation area/volume, board count
- `POST /roof/gutters/v2` — gutter length, downpipes, fittings

### MEP — basic preliminary calculators (v2, returns `CalculationResult`)

> These are preliminary estimates, not certified engineering designs (see warnings in each result).

- `POST /mep/hvac/heat-loss-basic/v2` — transmission + ventilation heat loss
- `POST /mep/electrical/load-basic/v2` — installed/demand/apparent power and current
- `POST /mep/plumbing/pipe-volume/v2` — water volume inside pipes

### Estimates (deterministic aggregation, no prices)

- `POST /estimates/aggregate-materials/v2` — aggregate materials across submitted `CalculationResult`s
- `POST /estimates/from-calculations/v2` — aggregate materials from stored calculations by id
- `POST /calculations/{calculation_id}/estimate` — basic estimate from a stored v2 calculation

### Work catalog (static reference content, no AI, no DB)

- `GET /work-types`, `GET /work-types/{slug}`
- `GET /work-subtypes`, `GET /work-subtypes/{slug}`
- `GET /calculation-templates`, `GET /calculation-templates/{code}`
- `GET /standards`, `GET /standards/{code}`
- `GET /method-statements/{work_subtype_slug}`
- `GET /qc-checks/{work_subtype_slug}`
- `GET /safety-rules/{work_subtype_slug}`

### AI

- `POST /ai/explain-calculation/{calculation_id}` — AI explanation of stored calculation
- `GET /ai/logs` — AI request logs
- `GET /ai/logs/{log_id}` — AI request log detail
- `POST /ai/chat` — AI chat (explains results; does not calculate)
- `GET /ai/chat/logs` — AI chat logs
- `GET /ai/chat/logs/{log_id}` — AI chat log detail

> AI scope is unchanged: it explains existing `CalculationResult` data and answers questions. All quantities are computed deterministically by backend services.

## Planned endpoints (not implemented)

- `/insulation/*` and `/waterproofing/*` as standalone module-level endpoints (currently covered within foundation/facade/floors/roof)
- `/finishing/*` interior finishing calculators
- `/materials/*` material catalog with real prices
- `/projects/*` project-level workflow and stage aggregation
