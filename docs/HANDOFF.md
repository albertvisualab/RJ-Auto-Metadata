# Handoff — RJ Auto Metadata

> Continuity document for agent sessions. Read this to resume work without full chat history.

## Phase 0 Status: Complete

### What Was Done

- Updated `.gitignore` — added `logs`, `api_jikaperlu/`, `*.env`, `.env*`, `.env.local`
- Created `dev` branch from `main` as integration baseline
- Created `task/docs-governance` branch from `dev`
- Created `AGENTS.md` at repository root
- Created documentation files in `docs/`:
  - `ARCHITECTURE.md` — system design, provider table, request flow
  - `GIT_POLICY.md` — branch model, commit format, merge/push rules
  - `CURRENT_STATE.md` — v3.11.3 snapshot, providers, technical debt
  - `HANDOFF.md` — this file
  - `ROADMAP.md` — phased refactoring plan

### What Is NOT Done

- No product code changed (no `src/`, `main.py`, or script modifications)
- Backend refactor not started (Gemini migration, dead code removal, etc.)
- UI refactor not started (layout changes, Fetch button, Custom provider, etc.)

## Next Phase

**Phase 1** — `task/refactor-backend`

Branch from `dev`. See `docs/ANALISYS_REFACTORING.md` Section 11 for full item list.

### Phase 1 Scope (B1–B9, U1–U2)

- **B1**: Refactor `gemini_api.py` to OpenAI SDK + compat endpoint (~600 lines removed)
- **B2**: OpenAI dead code cleanup (keep Responses API)
- **B3**: Remove all hardcoded model presets from `*_api.py` files
- **B4**: Centralize `_clean_json_text()` to `src/utils/json_utils.py`
- **B5**: Remove Gemini Auto Rotation (part of B1)
- **B6**: Add `PROVIDER_BASE_URLS` constant to `provider_manager.py`
- **B7**: Add `"Custom"` provider handler
- **B8**: Refactor if-elif dispatch chain in `provider_manager.py`
- **B9**: Fix duplicate `gpt-4o` in `_STRUCTURED_OUTPUT_MODEL_PREFIXES`
- **U1**: Add terminal log severity filter in `src/utils/logging.py`
- **U2**: Create `src/utils/json_utils.py`

## Key Decisions Already Made

These decisions are final. Do not re-discuss or change them.

| Decision | Resolution |
|---|---|
| Gemini endpoint | Migrate to OpenAI compat (`v1beta/openai/`) |
| OpenAI endpoint | Stay on Responses API (`/v1/responses`) |
| Model filtering | No filter — fetch all, user decides |
| Gemini Auto Rotation | Remove entirely |
| Custom provider | Add as 6th option with editable URL field |
| Auto Retry | Hardcode `True` in backend, remove UI toggle |
| `_clean_json_text()` | Centralize to `src/utils/json_utils.py` |

## Important Files to Read Before Phase 1

1. `AGENTS.md`
2. `docs/CURRENT_STATE.md`
3. `docs/ARCHITECTURE.md`
4. `docs/ANALISYS_REFACTORING.md` (sections 1–8 for backend scope)
