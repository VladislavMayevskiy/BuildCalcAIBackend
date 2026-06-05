This folder is the target home for database wiring (`SessionLocal`, `get_db`, declarative `Base`).

## Current status

Planned, partially scaffolded.

To avoid risky import churn, the current working DB module still lives in:

- `app/database.py`

`app/db/database.py` currently re-exports from `app.database`.

