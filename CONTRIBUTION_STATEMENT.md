# Contribution Statement

**Team:** shahinsafarli / Emil-Jafarov-06 / Jeyhunaa
**Topic:** Topic 4 — Async Research Assistant
**Repository:** [https://github.com/shahinsafarli/async-research-assistant](https://github.com/shahinsafarli/async-research-assistant)
**Final tag:** `v1.0-final`
**Submission date:** 2026-05-23

---

## Member A — Shahin Safarli (`@shahinsafarli`)

**Owned (sole author of these files / PRs):**
- `src/config.py` — pydantic-settings configuration with typed environment variables
- `src/cli/` — CLI commands (`ask`, `history`) and researcher package entry point
- `tests/` — unified offline testing framework covering config, storage, service, researcher, concurrency, CLI, and utils modules
- Project scaffolding: `.gitignore`, GitHub PR template, topic-4 template (AI module, smoke tests, data, env example)
- `src/storage/postgres_repository.py` — PostgreSQL storage backend integrated alongside the existing SQLite layer, with no changes to SQLite-related files; database configuration extended in `src/config.py` to support both backends
- PRs: #1, #7, #9, #12 (`shahin/postgres-storage`)

**Co-owned (paired or substantially edited):**
- Repository initialization and branch strategy (with all members)
- `src/storage/` — co-owns storage layer after extending it with PostgreSQL support (original SQLite implementation by Jeyhuna remains unchanged)

**Reviewed (PRs reviewed and merged):**
- PRs: #1 (merged from `emil/config-and-models`), #9 (authored and merged `shahin/combined-testing-suite`)

**Approximate share of commits:** 40%

---

## Member B — Emil Jafarov (`@Emil-Jafarov-06`)

**Owned (sole author of these files / PRs):**
- `src/config.py` initial scaffold (PR #1, `emil/config-and-models`)
- `src/services/ai_service.py` — AI service with retry logic and structured logging
- `src/concurrency/` — async orchestrator with per-source timeouts and graceful degradation; core researcher logic
- `app/` — Streamlit application and Docker setup (`Dockerfile`, `docker-compose`)
- `README.md` — project overview, setup instructions, usage examples, and environment configuration guide
- `docs/report.pdf` / `docs/report.md` — full project report covering architecture, design decisions, async patterns, and evaluation
- PRs: #3, #6, #11, #13 (`emil/readme-and-report`)

**Co-owned (paired or substantially edited):**
- `docs/architecture.md` review (PR #2, merged by Emil)

**Reviewed (PRs reviewed and merged):**
- PRs: #2 (merged `jeyhuna/architecture-docs`)

**Approximate share of commits:** 30%

---

## Member C — Jeyhuna Sevdiyeva (`@Jeyhunaa`)

**Owned (sole author of these files / PRs):**
- `docs/architecture.md` and `src/__main__.py` entry point
- `src/storage/` — SQLite storage repository with session persistence
- `src/services/cache_service.py` — TTL cache service
- `src/utils/search_query.py` — search query utility
- `scripts/bench.py` — benchmarking script
- `scripts/demo.py` — demo script for project demonstration
- `docs/presentation.pptx` — project presentation slides covering problem statement, architecture, implementation highlights, and demo walkthrough
- `CONTRIBUTION_STATEMENT.md` — this file; documents individual contributions, commit ownership, and AI tool disclosure for the full team
- PRs: #2, #4, #5, #8, #14 (`jeyhuna/presentation-and-contribution`)

**Co-owned (paired or substantially edited):**
- Storage layer integration with CLI history command (with Shahin)

**Reviewed (PRs reviewed and merged):**
- PRs: #4, #5, #8 (authored and merged own PRs)

**Approximate share of commits:** 30%

---

## AI tool disclosure (also in §10 of the report)

We used AI coding assistants as follows. Each item lists the module, the assistant, and what the team did with the output.

| Module / file | Assistant | What we did with it |
|---|---|---|
| `src/services/ai_service.py` | Claude | Suggested retry/backoff structure; team revised error handling and integrated project-specific logging format. |
| `src/concurrency/orchestrator.py` | Claude | Drafted initial async task structure; team rewrote per-source timeout logic and graceful degradation after integration testing. |
| `tests/` (unified suite) | Claude | Proposed test scaffolding; team reviewed all cases, removed mocks that didn't match actual interfaces, and added concurrency and CLI edge-case tests. |

We affirm that we **can defend every line of code** in this repository during the oral defense. "The AI wrote it" is not an answer we will use.

---

## Signatures

By signing below, we affirm that:
- The contributions described above are accurate.
- The commit percentages reflect actual work, not artificially split commits.
- Every line of code in the repository can be defended by at least one team member.
- AI assistant usage has been disclosed as described above.

| Member | Signature | Date |
|---|---|---|
| Shahin Safarli | __________________________ | __________ |
| Emil Jafarov | __________________________ | __________ |
| Jeyhuna Sevdiyeva | __________________________ | __________ |
