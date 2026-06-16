# BuildCalcAi Backend Architecture

## Current layered architecture (today)

This repository is intentionally simple and keeps deterministic calculator logic separated from HTTP routes:

- **Routes (`app/api/routes/`)**: HTTP layer only (auth dependencies, DB session, status codes). No formulas. Routers per module: `earthworks`, `foundation`, `concrete`, `rebar`, `walls`, `facade`, `floors`, `tiles`, `roofing`, `mep`, `estimates`, `work_catalog`, plus rooms/calculations/auth/users/ai.
- **Services (`app/services/`)**: deterministic calculation logic. Every v2 calculator returns a `CalculationResult` (`calculation_type`, `steps`, `materials`, `assumptions`, `warnings`); formulas live only here. Also hosts the static `work_catalog_service`, `estimate_service` (incl. material aggregation), and AI helpers. No AI/OpenAI inside calculators.
- **Schemas (`app/schemas/`)**: Pydantic request/response models used by both routes and services. Inputs validate with `@model_validator(mode="after")`; the shared result contract is `calculation_result.py`.
- **Models (`app/models/`)**: SQLAlchemy ORM entities (users, rooms, calculation history, AI logs). All v2 calculator routes persist a `Calculation` history row.
- **DB wiring (`app/database.py`)**: SQLAlchemy engine/session and `get_db`.
- **Security (`app/oauth2.py`)**: JWT helpers and `get_current_user`. Calculator endpoints require auth; the static work-catalog `GET` endpoints are public reference data.

## Target direction: "House from 0 to 100"

The project is moving toward a modular, domain-driven structure where each construction stage has its own deterministic module:

- `app/domain/<module>/` (planned placeholders today)
  - `schemas.py`, `services.py`, `validators.py`, `constants.py`
  - `README.md` describing the module and its planned calculators

### Why keep `app/services/` for now

Existing calculators are working and tested. Moving them into domain modules is a future refactor that would involve more changes than a safe re-organization. For now:

- **All working deterministic logic remains in `app/services/`.**
- **All working endpoints remain implemented via `app/api/routes/`.**
- `app/domain/` exists as a placeholder for gradual migration.

## API package layout

`app/api/routes/` is the canonical home for existing routers.

To avoid breaking older imports, the previous modules in `app/routes/` remain as compatibility shims that re-export `router` from the new locations.

## Core/db wrappers

To minimize risk, `app/core/` and `app/db/` currently provide wrappers and READMEs; the canonical modules still live in:

- `app/config.py`
- `app/oauth2.py`
- `app/database.py`

