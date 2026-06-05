# BuildCalcAi Backend — Project Status and Roadmap

## 1. Product Vision — "House from 0 to 100"

BuildCalcAi має стати системою, яка підтримує повний цикл кількісного обліку будівництва: від підготовки майданчика до фінальних внутрішніх оздоблювальних робіт.

Платформа повинна давати користувачу відповіді на питання:
- Скільки матеріалів потрібно?
- Чому саме така кількість?
- Які припущення використано у розрахунках?
- Які попередження потрібно врахувати?
- Яка приблизна вартість?
- Які матеріали включені у розрахунок?
- Звідки взято ціни?
- Коли останній раз оновлювалися ціни?
- До якої стадії будівництва належить розрахунок?

Системна ідея: AI не робить первинні обчислення. Бекенд повинен виконувати детерміністичні розрахунки, зберігати їх, а AI — пояснювати, допомагати з питаннями, уточнювати дані і маршрутизувати запити.

## 2. Current State

### Implemented
- JWT-аутентифікація: `/login`, `/users/`
- Користувачі, кімнати, історія розрахунків
- Room CRUD: створення, отримання, оновлення, видалення
- Room calculation v1: `POST /calculate`
- Room calculation v2: `POST /calculate/v2`
- Strip foundation v1: `POST /foundation/strip`
- Strip foundation v2: `POST /foundation/strip/v2`
- AI explanation: `POST /ai/explain-calculation/{calculation_id}`
- AI request logs: `GET /ai/logs`, `GET /ai/logs/{log_id}`
- AI chat routes: `POST /ai/chat`, `GET /ai/chat/logs`, `GET /ai/chat/logs/{log_id}`
- `CalculationResult` як стандартна ціль для v2-розрахунків

### In Progress
- AI chat реалізований у коді, але prompt і проєктна контекстуалізація потребують допрацювання
- `CalculationResult` існує як стандартна структура, але ще не заповнений універсально для всіх модулів
- strip foundation модуль розпочатий, але не має повної дорожньої карти для фундаментного блоку

### Planned
- Додати slab foundation, pile foundation, concrete/rebar/formwork модулі
- Створити матеріальний каталог, систему цін та генератор кошторисів
- Впровадити проектний workflow з `Project` та агрегованими етапами
- Додати структуровані AI-відповіді та prompt control
- Зробити інтернет-пошук цін лише як майбутню опцію

### Future / Advanced
- RAG / embeddings / семантичний пошук
- AI tool calling та agent loop
- Онлайн фідинг цін через постачальників / API
- Підтримка експорту PDF / відображення свіжості ціни
- Профільні ML/Deep Learning модулі для AI оцінювання

## 3. Current Architecture

### Routes
- `app/api/routes/auth.py` — логін та JWT
- `app/api/routes/users.py` — реєстрація користувача
- `app/api/routes/rooms.py` — CRUD кімнат і розрахунки для збережених кімнат
- `app/api/routes/calculations.py` — розрахунки кімнат і історія
- `app/api/routes/foundation.py` — стрічковий фундамент
- `app/api/routes/ai.py` — AI пояснення, логування, чат
- `app/main.py` — збирання маршрутизаторів, корінь `/`

> Note: `app/routes/*` remains as **compatibility shims** (re-export `router`) to avoid breaking old imports.

### Schemas
- `app/schemas/User.py`
- `app/schemas/Room.py`
- `app/schemas/calculation.py`
- `app/schemas/calculation_result.py`
- `app/schemas/strip_foundation.py`
- `app/schemas/ai.py`

### Services
- `app/services/calculation_service.py`
- `app/services/strip_foundation_service.py`
- `app/services/openai_service.py`
- `app/services/ai_prompt_service.py`

### Models
- `app/models/users.py`
- `app/models/room.py`
- `app/models/calculation_history.py`
- `app/models/ai_request_log.py`
- `app/models/ai_chat.py`

### Database
- `app/database.py`
- `app/config.py`
- Alembic migrations у `alembic/versions/`

### Planned domain structure (placeholders)

`app/domain/*` folders are created as **placeholders only** for the "House from 0 to 100" roadmap.
They contain only docstrings/TODOs and **no business logic** yet.

### Tests
- юніт тести для калькуляторів у `tests/`
- поки що без route-, auth-, AI- та інтеграційних тестів

## 4. Current Implemented API Endpoints

| Method | Path | Auth | Purpose | Response |
|---|---|---|---|---|
| GET | `/` | No | Health check | JSON |
| POST | `/login` | No | Отримати JWT токен | `access_token`, `token_type` |
| POST | `/users/` | No | Реєстрація користувача | `UserResponse` |
| POST | `/rooms/` | Yes | Створення кімнати | `RoomResponse` |
| GET | `/rooms/` | Yes | Список кімнат | `list[RoomResponse]` |
| GET | `/rooms/{room_id}` | Yes | Отримати кімнату | `RoomResponse` |
| PATCH | `/rooms/{room_id}` | Yes | Оновити кімнату | `RoomResponse` |
| DELETE | `/rooms/{room_id}` | Yes | Видалити кімнату | `204` |
| POST | `/rooms/{room_id}/calculate` | Yes | Розрахунок для збереженої кімнати | `CalculationResponse` |
| GET | `/rooms/{room_id}/calculations` | Yes | Історія розрахунків кімнати | `list[CalculationHistoryResponse]` |
| GET | `/calculations/history` | Yes | Історія користувача | `list[CalculationHistoryResponse]` |
| POST | `/calculate` | Yes | Room calc v1 | `CalculationResponse` |
| POST | `/calculate/v2` | Yes | Room calc v2 | `CalculationResult` |
| POST | `/foundation/strip` | Yes | Strip foundation v1 | `StripFoundationResponse` |
| POST | `/foundation/strip/v2` | Yes | Strip foundation v2 | `CalculationResult` |
| POST | `/ai/explain-calculation/{calculation_id}` | Yes | AI explain calculation | `AIExplanationResponse` |
| GET | `/ai/logs` | Yes | AI explain logs | `list[AIRequestLogResponse]` |
| GET | `/ai/logs/{log_id}` | Yes | AI explain log detail | `AIRequestLogResponse` |
| GET | `/ai/chat/logs` | Yes | AI chat logs | `list[AIChatResponse]` |
| GET | `/ai/chat/logs/{log_id}` | Yes | AI chat log detail | `AIChatResponse` |
| POST | `/ai/chat` | Yes | General AI chat | `AIResponse` |

## 5. Current Calculation System

### Room calculation v1
- `app/services/calculation_service.calculate_room`
- Вхідні дані: `length`, `width`, `height`, `windows_area`, `doors_area`
- Віддає: `floor_area`, `ceiling_area`, `wall_area`, `wall_area_with_reserve`, `paint_liters`, `tile_required_sqm`
- Валідація: відкриття не можуть перевищувати площу стін.

### Room calculation v2
- `app/services/calculation_service.calculate_room_v2`
- Повертає `CalculationResult`
- Структура включає:
  - `calculation_type`
  - `steps`
  - `materials`
  - `assumptions`
  - `warnings`

### Strip foundation v1
- `app/services/strip_foundation_service.calculate_strip_foundation`
- Віддає `perimeter`, `concrete_volume`, `concrete_volume_with_reserve`

### Strip foundation v2
- `app/services/strip_foundation_service.calculate_strip_foundation_v2`
- Повертає `CalculationResult`
- Є кроки, `materials`, `assumptions`

### Why CalculationResult
- уніфікує дані для фронтенду та AI
- зберігає послідовність кроків і формул
- робить результат придатним для матеріалів та кошторисів
- дозволяє додавати warnings і assumptions

## 6. Current AI Integration

### OpenAI service
- `app/services/openai_service.py`
- `OpenAI(api_key=settings.openai_api_key)`
- `client.responses.create(model="gpt-4.1-mini", input=prompt)`
- Повертає `response.output_text`
- Немає таймаутів, retry чи logging latency

### Prompt service
- `app/services/ai_prompt_service.py`
- Генерує prompt для пояснення збереженого розрахунку
- Немає окремого prompt builder для проєктного чату

### AI explanation endpoint
- `POST /ai/explain-calculation/{calculation_id}`
- Забирає `Calculation` з бази
- Будує prompt з `input_data` та `result_data`
- Повертає текстове пояснення
- Логує через `AIRequestLog`

### AI request logging
- `app/models/ai_request_log.py`
- Зберігає `prompt`, `response`, `error_message`, `status`, `calculation_id`
- Поки що без `prompt_version`, `model`, `tokens`, `latency`

### AI chat
- `POST /ai/chat` присутній у коді
- Логує в `app/models/ai_chat.py`
- Повертає `AIResponse`
- Потребує project-aware prompt та більш чітких обмежень

### AI role
- AI пояснює, відповідає, задає уточнюючі питання
- AI не робить детерміністичні розрахунки
- Backend виконує арифметику

## 7. Current Database Entities

### Users
- `app/models/users.py`
- `id`, `name`, `email`, `hashed_password`, `created_at`

### Room
- `app/models/room.py`
- `id`, `user_id`, `name`, `length`, `width`, `height`, `room_type`, `doors_area`, `windows_area`, `created_at`

### Calculation
- `app/models/calculation_history.py`
- `id`, `input_data`, `result_data`, `user_id`, `room_project_id`, `calculation_type`, `created_at`

### AIRequestLog
- `app/models/ai_request_log.py`
- Логи AI пояснень для розрахунків

### AIChat
- `app/models/ai_chat.py`
- Логи AI чату

### Немає зараз
- `Project`, `Estimate`, `Material`, `MaterialCategory`, `MaterialPrice`, `Supplier`, `PriceSource`, `PromptVersion`
- RAG / embeddings / семантичний пошук

## 8. Current Tests

### Існуючі
- `tests/test_calculation_service.py`
- `tests/test_calculation_service_perimeter.py`
- `tests/test_calculation_service_v2.py`
- `tests/test_strip_foundation_service.py`

### Покриття
- Основні калькулятори
- `CalculationResult` структура

### Відсутні
- API integration tests
- Auth tests
- Room CRUD tests
- Calculation history route tests
- AI endpoint tests
- OpenAI mocking tests
- AI chat tests
- Project/estimate tests

## 9. Current Gap

BuildCalcAi має добру технічну основу, але ще не є повноцінним калькулятором будівництва.

### Має бути зроблено
- strip foundation модуль розпочато, але неповний
- немає slab foundation, pile foundation, rebar, formwork
- немає фасадних, внутрішніх, дахових модулів
- немає матеріального каталогу та цінової системи
- немає агрегованого кошторису
- немає повноцінного проектного workflow
- немає структурованих AI-відповідей
- немає tool calling

## 10. House from 0 to 100 — Product Modules

### A. Site Preparation / Earthworks
Planned calculators:
- excavation volume
- trench volume
- soil removal volume
- sand/gravel backfill
- compacted layer volume

Suggested endpoints:
- `POST /earthworks/excavation/v2`
- `POST /earthworks/trench/v2`
- `POST /earthworks/backfill/v2`

### B. Foundation Module
Current:
- strip foundation v1/v2

Planned:
- strip foundation advanced
- slab foundation
- pile foundation
- concrete volume
- rebar quantity
- stirrups
- formwork area
- gravel/sand cushion
- waterproofing
- foundation insulation
- foundation estimate

Suggested endpoints:
- `POST /foundation/strip/v2`
- `POST /foundation/slab/v2`
- `POST /foundation/pile/v2`
- `POST /foundation/rebar/v2`
- `POST /foundation/formwork/v2`
- `POST /foundation/waterproofing/v2`
- `POST /foundation/estimate/v2`

### C. Concrete and Reinforcement Module
Planned:
- concrete volume by shape
- concrete mass approximation
- rebar length
- rebar weight by diameter
- mesh area
- overlap/lap length
- stirrups count
- binding wire estimate

Suggested endpoints:
- `POST /concrete/volume/v2`
- `POST /rebar/linear/v2`
- `POST /rebar/mesh/v2`
- `POST /rebar/stirrups/v2`

### D. Walls / Masonry Module
Planned:
- block wall quantity
- brick quantity
- mortar quantity
- wall area minus openings
- lintel approximate count
- waste factor

Suggested endpoints:
- `POST /walls/blocks/v2`
- `POST /walls/bricks/v2`
- `POST /walls/mortar/v2`

### E. Floor / Slab / Structure Module
Planned:
- floor slab concrete volume
- screed
- insulation under screed
- vapor barrier
- reinforcement mesh

Suggested endpoints:
- `POST /floors/slab/v2`
- `POST /floors/screed/v2`
- `POST /floors/insulation/v2`

### F. Roofing Module
Planned:
- roof area by slope
- roof sheets / metal tile / ceramic tile
- underlayment membrane
- insulation
- battens
- rafters approximate material
- gutters and downpipes
- fasteners

Suggested endpoints:
- `POST /roof/area/v2`
- `POST /roof/covering/v2`
- `POST /roof/membrane/v2`
- `POST /roof/insulation/v2`
- `POST /roof/gutters/v2`

### G. Facade Module
Planned:
- facade area minus openings
- insulation boards
- adhesive
- mesh
- plaster
- primer
- facade paint
- decorative plaster

Suggested endpoints:
- `POST /facade/area/v2`
- `POST /facade/insulation/v2`
- `POST /facade/plaster/v2`
- `POST /facade/paint/v2`
- `POST /facade/full-system/v2`

### H. Windows and Doors Module
Planned:
- opening area summary
- slopes area
- mounting foam estimate
- sill lengths
- trim quantities

Suggested endpoints:
- `POST /openings/summary/v2`
- `POST /openings/slopes/v2`
- `POST /openings/materials/v2`

### I. Interior Finishing Module
Planned:
- interior plaster
- putty
- primer
- paint
- wallpaper
- drywall partitions
- drywall ceilings
- joint tape / screws / profiles

Suggested endpoints:
- `POST /finishing/plaster/v2`
- `POST /finishing/putty/v2`
- `POST /finishing/primer/v2`
- `POST /finishing/paint/v2`
- `POST /finishing/wallpaper/v2`
- `POST /drywall/partition/v2`
- `POST /drywall/ceiling/v2`

### J. Tile and Flooring Module
Planned:
- floor tiles
- wall tiles
- adhesive
- grout
- laminate
- parquet
- vinyl
- baseboard

Suggested endpoints:
- `POST /tiles/floor/v2`
- `POST /tiles/wall/v2`
- `POST /tiles/adhesive/v2`
- `POST /tiles/grout/v2`
- `POST /floors/laminate/v2`
- `POST /floors/baseboard/v2`

### K. Waterproofing / Insulation Module
Planned:
- bathroom waterproofing
- foundation waterproofing
- roof insulation
- facade insulation
- floor insulation
- membrane overlaps

Suggested endpoints:
- `POST /waterproofing/bathroom/v2`
- `POST /waterproofing/foundation/v2`
- `POST /insulation/facade/v2`
- `POST /insulation/roof/v2`
- `POST /insulation/floor/v2`

## 11. Standard Calculator Contract

Всі нові калькулятори повинні повертати `CalculationResult`.

Кожен `CalculationResult` має містити:
- `calculation_type`
- `steps`
- `materials`
- `assumptions`
- `warnings`

## 12. Material Quantity System

MaterialItem має бути нормалізованою для подальшого кошторису:
- `name`
- `quantity`
- `unit`
- `waste_percent`
- `category` (planned)
- `notes` (planned)
- `material_code` (planned)

Категорії:
- concrete
- rebar
- masonry
- plaster
- putty
- primer
- paint
- insulation
- roofing
- tiles
- flooring
- waterproofing
- fasteners
- auxiliary materials

## 13. Price and Estimate Roadmap

### Phase 1 — Quantity only
Поточний стан: більшість API повертає кількість матеріалів, але без цін.

### Phase 2 — Local material catalog
План:
- `Material`
- `MaterialCategory`
- `Unit`
- `MaterialPrice`
- `Supplier` (optional)

Поля:
- `name`
- `category`
- `unit`
- `default_price`
- `currency`
- `source`
- `updated_at`

### Phase 3 — Estimate generator
План:
- агрегувати `CalculationResult.materials`
- створювати `EstimateResult`
- враховувати `subtotal_materials`, `currency`, `assumptions`, `warnings`

### Phase 4 — Project-level estimate
План:
- `Project`
- `ProjectRoom`
- `ConstructionStage`
- агрегувати по фундаменту, стінам, даху, фасаду, внутрішньому оздобленню, підлозі

### Phase 5 — Internet price fetching
Майбутнє:
- fetch ціни з онлайн-магазинів / API постачальників
- перевіряти юридичні умови
- кешувати ціни
- зберігати `price source URL`, `supplier`, `updated_at`
- нормалізувати одиниці та валюту
- fallback на local catalog

## 14. Project-Level Workflow

1. Створити проект
2. Додати будівельні характеристики
3. Додати кімнати / зони
4. Обчислити фундамент
5. Обчислити стіни
6. Обчислити дах
7. Обчислити фасад
8. Обчислити внутрішнє оздоблення
9. Агрегувати матеріали
10. Застосувати ціни
11. Згенерувати кошторис
12. AI пояснює кошторис
13. Експорт PDF / звіт (planned)

Suggested planned endpoints:
- `POST /projects/`
- `GET /projects/`
- `GET /projects/{project_id}`
- `POST /projects/{project_id}/calculations`
- `POST /projects/{project_id}/estimate`
- `GET /projects/{project_id}/estimate`

## 15. Suggested Future Database Entities

### Project
- `id`, `user_id`, `name`, `description`, `created_at`
- групує кімнати, розрахунки, кошториси

### ProjectRoom
- `project_id`, `room_id`, `role`

### Building
- `footprint`, `height`, `stories`, `zone`

### ConstructionStage
- `project_id`, `stage_type`, `status`, `started_at`, `completed_at`

### Material
- `name`, `category_id`, `unit`, `default_price`, `source`, `updated_at`

### MaterialCategory
- `name`, `description`

### MaterialPrice
- `material_id`, `price`, `currency`, `supplier_id`, `updated_at`

### Supplier
- `name`, `website`, `contact`

### PriceSource
- `supplier_id`, `url`, `retrieved_at`, `valid_until`

### Estimate
- `project_id`, `title`, `currency`, `subtotal_materials`, `created_at`

### EstimateItem
- `estimate_id`, `material_id`, `quantity`, `unit`, `unit_price`, `line_total`

### PromptVersion
- `name`, `template`, `version`, `created_at`

### AIUsageLog
- `user_id`, `request_type`, `model`, `tokens`, `latency`, `cost`, `status`

## 16. Suggested Future Architecture

Рекомендована доменна організація:

```
app/domain/foundation/
  schemas.py
  services.py
  validators.py
  constants.py
app/domain/earthworks/
app/domain/walls/
app/domain/facade/
app/domain/finishing/
app/domain/floors/
app/domain/roofing/
app/domain/materials/
app/domain/estimates/
app/domain/projects/
```

Правило:
- `routes` відповідають за HTTP/auth/DB
- `services` виконують чисті калькуляції
- AI пояснює та маршрутизує, але не рахує

## 17. Immediate Next Tasks

- [ ] Finish `POST /ai/chat` prompt і project-aware поведінку
- [ ] Add AI chat tests
- [ ] Complete strip foundation v2 edge cases and warnings
- [ ] Add slab foundation v2 module and tests
- [ ] Add rebar calculator module and tests
- [ ] Add formwork calculator module and tests
- [ ] Add facade area/insulation calculators
- [ ] Define material catalog models and price schema
- [ ] Add `EstimateResult` schema
- [ ] Add generator from `CalculationResult.materials`
- [ ] Add local price support

## 18. AI Roadmap Connected to Product

### Current
- AI пояснює збережені розрахунки
- AI чат є, але потребує кращого prompt

### Next
- project-aware prompt для `/ai/chat`
- structured outputs
- intent detection / entity extraction
- missing field prompts
- tool calling
- AI estimate assistant
- RAG над будівельними нормами
- AI пояснює ціни без вигадування

## 19. Definition of Done for Any New Calculator

- schema існує
- service існує
- route існує
- response_model = `CalculationResult`
- формули реалізовані у бекенді
- є validation
- є assumptions
- є warnings
- є materials
- є stable `calculation_type`
- зберігається у history
- AI може пояснити результат

## 20. Definition of Done for Full House Estimate System

- є `Project` entity
- всі модулі можуть віддавати `CalculationResult`
- матеріали нормалізовані
- кошторис агрегує матеріали
- local prices підтримуються
- інтернет-ціни кешуються з джерелом і timestamp
- frontend бачить свіжість ціни
- AI пояснює, але не вигадує ціни
- PDF/export planned

## 21. AI / ML / Deep Learning Roadmap

### 1–10 = AI Engineer path inside this project
0. Current Level — FastAPI backend + DB + calculator services + OpenAI key
1. AI API Integration — models, tokens, errors, retries, streaming
2. Prompting & Context Control — system prompts, grounding, prompt templates
3. Structured Outputs — JSON schema, Pydantic validation, strict outputs
4. Intent Detection & Entity Extraction — parse user requests, missing fields
5. Tool Calling — AI selects calculator, backend executes it
6. AI Observability — logs, tokens, cost, latency, prompt versions
7. AI Evals — tests for parser/explainer/tool calling
8. RAG — embeddings, chunking, pgvector, semantic search, citations
9. Agents — tool loop, memory, audit logs, human-in-the-loop
10. Production AI Engineering — rate limits, quotas, fallback models, safety

### 11–16 = ML Engineer foundation
11. Data Engineering Basics
12. Math for ML
13. Classical ML
14. Feature Engineering & Model Evaluation
15. PyTorch Basics
16. Neural Networks

### 17–21 = Deep Learning Engineer path
17. Deep Learning
18. NLP / Transformers
19. Fine-tuning
20. MLOps
21. Advanced Deep Learning

## 22. Current Project Stage

Поточний проект знаходиться між:
- **Stage 1: AI API Integration**
- **Stage 2: Prompting & Context Control**
- **Early calculator standardization**

> `POST /ai/chat` присутній у коді, але його варто довести до проєктно-орієнтованої поведінки.

## 23. Suggested File Changes

- `app/schemas/ai.py`
- `app/services/ai_prompt_service.py`
- `app/routes/ai.py`
- `app/services/openai_service.py`
- `app/services/calculation_service.py`
- `app/services/strip_foundation_service.py`
- `app/models/ai_chat.py`
- `app/models/ai_request_log.py`
- `app/models/material.py` (planned)
- `app/models/estimate.py` (planned)
- `alembic/versions/*`
- `tests/test_ai_chat.py`
- `tests/test_ai_explain_calculation.py`
- `tests/test_estimates.py`
- `docs/PROJECT_STATUS_AND_ROADMAP.md`

## 24. Immediate Next Tasks

- [ ] Finish `/ai/chat` prompt and project-aware behavior
- [ ] Add AI chat integration tests
- [ ] Complete strip foundation v2 edge cases and warnings
- [ ] Add slab foundation v2 module and tests
- [ ] Add rebar calculator module and tests
- [ ] Add formwork calculator module and tests
- [ ] Add facade area/insulation calculators
- [ ] Define material catalog models and price schema
- [ ] Add `EstimateResult` schema
- [ ] Add generator from `CalculationResult.materials`
- [ ] Add local price support
