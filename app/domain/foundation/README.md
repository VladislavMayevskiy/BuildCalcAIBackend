Foundation module (planned).

## Purpose

Deterministic calculators for foundation-related quantities (concrete, geometry, reinforcement, waterproofing, insulation).

## Planned calculators

- strip foundation (advanced)
- slab foundation
- pile foundation
- formwork area
- rebar quantities (foundation scope)
- foundation waterproofing
- foundation insulation

## Planned endpoints

- `POST /foundation/*` (partially implemented today for strip foundation; other endpoints planned)

## Status

Planned as a domain module (placeholders only). Current working strip-foundation logic remains in `app/services/strip_foundation_service.py` and is exposed via `POST /foundation/strip` and `POST /foundation/strip/v2`.

