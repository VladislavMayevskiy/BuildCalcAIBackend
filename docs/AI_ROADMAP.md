# AI Roadmap

AI is intended to **explain and assist**, not to perform primary deterministic arithmetic.

## Stage 1 — Explanation (current)

- Explain stored deterministic calculations (`POST /ai/explain-calculation/{calculation_id}`).
- Log AI requests and responses.

## Stage 2 — Project-aware chat (planned)

- Chat grounded in project context (rooms, calculations, estimates).
- Better prompting and guardrails (no inventing measurements/prices).

## Stage 3 — Structured outputs (planned)

- Return validated JSON structures for explanations (summary, steps, assumptions, warnings).

## Stage 4 — Intent detection (planned)

- Detect user intent (which calculator is needed) from natural language.

## Stage 5 — Entity extraction (planned)

- Extract dimensions/material preferences into typed request schemas.

## Stage 6 — Tool calling / routing (planned)

- AI selects a tool (calculator), backend executes it deterministically, AI explains results.

## Stage 7 — Evals (planned)

- Golden tests for parser/router/explainer behavior.

## Stage 8 — RAG (planned)

- Ground answers in norms/manufacturer docs with citations.

## Stage 9 — Agents (planned)

- Multi-step workflows (project estimate building) with audit logs and safety constraints.

## Stage 10 — Production AI (planned)

- Observability (tokens/cost/latency), prompt versioning, rate limits, fallbacks, security hardening.

