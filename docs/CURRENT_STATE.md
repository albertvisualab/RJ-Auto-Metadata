# Current State — RJ Auto Metadata

> Snapshot at Phase 2 completion.

## Version

**3.11.3** (tagged `v3.11.3` on `main`)

## Branch Structure

- `main` — stable release baseline (v3.11.3)
- `dev` — integration branch (Phase 1 merged)
- `task/docs-governance` — Phase 0 work branch (merged to dev)
- `task/refactor-backend` — Phase 1 work branch (merged to dev)
- `task/refactor-ui` — Phase 2 work branch (current)

## Supported Providers

| Provider | Endpoint Type | Status |
|---|---|---|
| **Gemini** | OpenAI compat (`v1beta/openai/`) | Migrated in Phase 1 |
| **OpenAI** | Responses API (`/v1/responses`) | Unchanged |
| **OpenRouter** | Chat Completions | Unchanged |
| **Groq** | Chat Completions | Unchanged |
| **KoboiLLM** | Chat Completions | Unchanged |
| **Custom** | User-defined base URL | Added in Phase 1, UI added in Phase 2 |

## Technical Debt Resolved in Phase 1

- **Hardcoded model presets**: Removed from all 5 `*_api.py` files; `get_model_choices()` / `get_default_model()` stubbed for UI compat
- **Gemini native REST**: Replaced ~770-line SDK/REST dual path with ~300-line OpenAI SDK implementation
- **Duplicate `_clean_json_text()`**: Centralized to `src/utils/json_utils.py`; removed from `openai_api.py`, `openrouter_api.py`, `koboillm_api.py`
- **Gemini Auto Rotation**: Removed entirely (model rotation logic, cooldowns, locks)
- **Dead code**: Removed `calculate_smart_delay()`, `DEBUG_FORCE_FAILURE`, commented-out debug blocks
- **Noisy terminal output**: Added `_TERMINAL_PRINT_TAGS` filter — only warning/error/critical/success print to terminal
- **Duplicate `gpt-4o`**: Fixed in `_STRUCTURED_OUTPUT_MODEL_PREFIXES`
- **`PROVIDER_BASE_URLS`**: Added to `provider_manager.py` with all 6 provider URLs
- **Custom provider**: Added as 6th provider with `base_url_override` dispatch

## Changes in Phase 2

- **Load & Delete buttons**: Removed from UI; dead methods `_load_api_keys`, `_save_api_keys`, `_delete_selected_api_key`, `_toggle_api_key_visibility` removed
- **Auto Retry**: Switch removed from UI; `auto_retry_var` hardcoded to `True`
- **Save → Fetch**: Save button renamed to Fetch; wired to `_fetch_models()` with threaded model fetch
- **Base URL field**: Added, visible only when Custom provider is selected
- **Per-provider model state**: `_models_by_provider` dict tracks cached model lists per provider
- **Custom in dropdown**: "Custom" now appears in provider dropdown on startup
- **Settings persistence**: `models_by_provider` and `custom_base_url` saved/restored in config.json
- **`fetch_models()` stub**: Added to `provider_manager.py` — returns `[]`, real implementation deferred to Phase 3

## Remaining Technical Debt

- **`fetch_models()` stub**: Returns empty list; Phase 3 implements real `GET /v1/models` calls
- **Vision model filtering**: Not implemented; deferred to Phase 3

## Pending Phases

- **Phase 3**: Integration & Release — implement `fetch_models()`, final testing, merge to main

## Last Verified Working

- **Version**: 3.11.3
- **Platform**: Windows
- **Entry point**: `python main.py`
