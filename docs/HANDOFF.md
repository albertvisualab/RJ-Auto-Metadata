# Handoff — RJ Auto Metadata

> Continuity document for agent sessions. Read this to resume work without full chat history.

## Phase 0 Status: Complete

### What Was Done

- Updated `.gitignore` — added `logs`, `api_jikaperlu/`, `*.env`, `.env*`, `.env.local`
- Created `dev` branch from `main` as integration baseline
- Created `task/docs-governance` branch from `dev`
- Created `AGENTS.md` at repository root
- Created documentation files in `docs/`

## Phase 1 Status: Complete

### What Was Done

- **B1+B5**: Rewrote `gemini_api.py` — replaced ~770-line SDK/REST dual path + auto-rotation with ~300-line OpenAI SDK implementation using `v1beta/openai/` compat endpoint
- **B2**: Removed commented-out debug blocks from `openai_api.py`, `openrouter_api.py`, `groq_api.py`
- **B3**: Removed all hardcoded model presets (`*_MODEL_PRESETS`, `*_MODELS`, `DEFAULT_MODEL`) from all 5 provider files
- **B4**: Centralized `_clean_json_text()` to `src/utils/json_utils.py`; replaced local copies in `openai_api.py`, `openrouter_api.py`, `koboillm_api.py`
- **B6**: Added `PROVIDER_BASE_URLS` dict to `provider_manager.py` with all 6 provider URLs
- **B7+B8**: Added `PROVIDER_CUSTOM` and Custom provider entry to `_PROVIDERS`; added `base_url_override` parameter to `get_metadata()` dispatch; guarded all module calls against `None` for Custom
- **B9**: Fixed duplicate `gpt-4o` in `_STRUCTURED_OUTPUT_MODEL_PREFIXES` in `openai_api.py`
- **U1**: Added `_TERMINAL_PRINT_TAGS` filter to `src/utils/logging.py` — only warning/error/critical/success print to terminal
- **U2**: Created `src/utils/json_utils.py` with shared `_clean_json_text()`

### What Is NOT Done / Deferred to Phase 2

- `get_model_choices()` and `get_default_model()` in `provider_manager.py` are **stubbed** (return empty list / empty string) to avoid breaking `app.py` — Phase 2 will add Fetch button and dynamic model loading
- `app.py` was **not modified** — UI still references old model dropdown flow
- Auto Retry toggle still exists in UI — Phase 2 will hardcode `True` and remove toggle

## Phase 2 Status: Complete

### What Was Done

- **UI-1**: Removed Load and Delete buttons; removed dead methods `_load_api_keys`, `_save_api_keys`, `_delete_selected_api_key`, `_toggle_api_key_visibility`
- **UI-2**: Hardcoded `auto_retry_var` to `True`; removed Auto Retry switch from layout
- **UI-3**: Renamed Save button → Fetch; added `_fetch_models()` with threaded model fetch and `_apply_fetched_models()`; added `fetch_models()` stub to `provider_manager.py`
- **UI-4**: Added Base URL entry field, visible only when Custom provider is selected; added `_update_base_url_visibility()` method
- **UI-5**: Added `_models_by_provider` dict for per-provider model state; updated `_refresh_provider_models()` to use cached models
- **UI-6**: Added "Custom" to `available_providers` list on startup
- **UI-7**: Persisted `models_by_provider` and `custom_base_url` in config.json via `_save_settings()` / `_load_settings()`

### What Is NOT Done / Deferred to Phase 3

- `fetch_models()` in `provider_manager.py` is a **stub** (returns `[]`) — Phase 3 implements real `GET /v1/models` API calls
- Vision model filtering not implemented — deferred to Phase 3

## Next Phase

**Phase 3** — Integration & Release

Implement `fetch_models()` with real API calls, final integration testing across all providers, merge to main.

## Key Decisions Already Made

These decisions are final. Do not re-discuss or change them.

| Decision | Resolution |
|---|---|
| Gemini endpoint | Migrated to OpenAI compat (`v1beta/openai/`) |
| OpenAI endpoint | Stays on Responses API (`/v1/responses`) |
| Model filtering | No filter — fetch all, user decides |
| Gemini Auto Rotation | Removed entirely |
| Custom provider | Added as 6th option; dispatches via openrouter-style handler |
| Auto Retry | Hardcoded `True` in Phase 2, UI toggle removed |
| `_clean_json_text()` | Centralized to `src/utils/json_utils.py` |
| Load/Delete/Save buttons | Removed in Phase 2; replaced with Check + Fetch |

## Important Files to Read Before Phase 3

1. `AGENTS.md`
2. `docs/CURRENT_STATE.md`
3. `docs/ARCHITECTURE.md`
4. `docs/ANALISYS_REFACTORING.md` (sections 3, 7 for model fetch)
