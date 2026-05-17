# Current State — RJ Auto Metadata

> Snapshot at Phase 1 completion.

## Version

**3.11.3** (tagged `v3.11.3` on `main`)

## Branch Structure

- `main` — stable release baseline (v3.11.3)
- `dev` — integration branch (created in Phase 0)
- `task/docs-governance` — Phase 0 work branch (merged to dev)
- `task/refactor-backend` — Phase 1 work branch (current)

## Supported Providers

| Provider | Endpoint Type | Status |
|---|---|---|
| **Gemini** | OpenAI compat (`v1beta/openai/`) | Migrated in Phase 1 |
| **OpenAI** | Responses API (`/v1/responses`) | Unchanged |
| **OpenRouter** | Chat Completions | Unchanged |
| **Groq** | Chat Completions | Unchanged |
| **KoboiLLM** | Chat Completions | Unchanged |
| **Custom** | User-defined base URL | Added in Phase 1 |

## Technical Debt Resolved in Phase 1

- **Hardcoded model presets**: Removed from all 5 `*_api.py` files; `get_model_choices()` / `get_default_model()` stubbed for UI compat (Phase 2 adds Fetch button)
- **Gemini native REST**: Replaced ~770-line SDK/REST dual path with ~300-line OpenAI SDK implementation
- **Duplicate `_clean_json_text()`**: Centralized to `src/utils/json_utils.py`; removed from `openai_api.py`, `openrouter_api.py`, `koboillm_api.py`
- **Gemini Auto Rotation**: Removed entirely (model rotation logic, cooldowns, locks)
- **Dead code**: Removed `calculate_smart_delay()`, `DEBUG_FORCE_FAILURE`, commented-out debug blocks
- **Noisy terminal output**: Added `_TERMINAL_PRINT_TAGS` filter — only warning/error/critical/success print to terminal
- **Duplicate `gpt-4o`**: Fixed in `_STRUCTURED_OUTPUT_MODEL_PREFIXES`
- **`PROVIDER_BASE_URLS`**: Added to `provider_manager.py` with all 6 provider URLs
- **Custom provider**: Added as 6th provider with `base_url_override` dispatch

## Remaining Technical Debt

- **UI model dropdown**: Currently receives empty list from stubbed `get_model_choices()` — Phase 2 will add Fetch button
- **Auto Retry toggle**: Still exists as UI switch — Phase 2 will remove and hardcode `True`
- **UI layout**: Provider/Model dropdowns not yet restructured — Phase 2

## Pending Phases

- **Phase 2**: UI refactor (`task/refactor-ui`) — items UI1–UI11
- **Phase 3**: Integration & Release

## Last Verified Working

- **Version**: 3.11.3
- **Platform**: Windows
- **Entry point**: `python main.py`
