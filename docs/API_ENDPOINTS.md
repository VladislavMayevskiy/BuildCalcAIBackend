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

### Foundation

- `POST /foundation/strip` — strip foundation v1
- `POST /foundation/strip/v2` — strip foundation v2

### AI

- `POST /ai/explain-calculation/{calculation_id}` — AI explanation of stored calculation
- `GET /ai/logs` — AI request logs
- `GET /ai/logs/{log_id}` — AI request log detail
- `POST /ai/chat` — AI chat (if enabled in repo; currently present)
- `GET /ai/chat/logs` — AI chat logs
- `GET /ai/chat/logs/{log_id}` — AI chat log detail

## Planned endpoints (not implemented)

Future modules will add endpoints under:

- `/earthworks/*`
- `/concrete/*`
- `/rebar/*`
- `/walls/*`
- `/facade/*`
- `/roofing/*`
- `/insulation/*`
- `/waterproofing/*`
- `/finishing/*`
- `/tiles/*`
- `/floors/*`
- `/materials/*`
- `/estimates/*`
- `/projects/*`

