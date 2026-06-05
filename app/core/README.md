This folder is the target home for cross-cutting concerns (configuration, security, logging).

## Current status

Planned, partially scaffolded.

To avoid risky import churn, the current working modules still live in:

- `app/config.py`
- `app/oauth2.py`
- `app/database.py`

`app/core/*.py` currently provides light wrappers around these modules.

