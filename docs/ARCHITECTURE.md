# BuildCalcAi Backend Architecture

## Current layered architecture (today)

This repository is intentionally simple and keeps deterministic calculator logic separated from HTTP routes:

- **Routes (`app/api/routes/`)**: HTTP layer only (auth dependencies, DB session, status codes). No formulas.
- **Services (`app/services/`)**: deterministic calculation logic (room calculation v1/v2, strip foundation v1/v2) and AI helpers.
- **Schemas (`app/schemas/`)**: Pydantic request/response models used by both routes and services.
- **Models (`app/models/`)**: SQLAlchemy ORM entities (users, rooms, calculation history, AI logs).
- **DB wiring (`app/database.py`)**: SQLAlchemy engine/session and `get_db`.
- **Security (`app/oauth2.py`)**: JWT helpers and `get_current_user`.

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

