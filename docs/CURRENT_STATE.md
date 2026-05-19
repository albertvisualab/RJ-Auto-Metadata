# Current State — RJ Auto Metadata

> Snapshot at Phase 4B completion.

## Version

**3.11.3** (tagged `v3.11.3` on `main`)

## Branch Structure

- `main` — stable release baseline (v3.11.3)
- `dev` — integration branch (Phase 4A complete at `115b3fd`)
- `task/docs-governance` — Phase 0 work branch (merged to dev)
- `task/refactor-backend` — Phase 1 work branch (merged to dev)
- `task/refactor-ui` — Phase 2 work branch (merged to dev)
- `task/add-providers` — Phase 4A work branch (merged to dev)
- `task/dynamic-prompt-builder` — Phase 4B work branch (current)

## Supported Providers

| Provider | Endpoint Type | Status |
|---|---|---|
| **Gemini** | OpenAI compat (`v1beta/openai/`) | Migrated in Phase 1 |
| **OpenAI** | Responses API (`/v1/responses`) | Unchanged |
| **OpenRouter** | Chat Completions | Unchanged |
| **Groq** | Chat Completions | Unchanged |
| **KoboiLLM** | Chat Completions | Unchanged |
| **Mistral** | OpenAI compat (`/v1`) | Added in Phase 4A |
| **Blackbox** | OpenAI compat (`/`) | Added in Phase 4A |
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

## Changes in Phase 3

- **`fetch_models()` implemented**: Real implementation using OpenAI SDK `client.models.list()` for all providers; filters non-generative models (embeddings, tts, whisper, dall-e, legacy completions)
- **CTkScrollableDropdown**: Vendored Akascape/CTkScrollableDropdown (MIT) into `src/ui/CTkScrollableDropdown/`; attached to all 5 CTkComboBox dropdowns for scrollable popup behavior; `command` callbacks passed through for provider and theme
- **Per-provider key/model sync**: `_on_provider_change` now syncs textbox → `_actual_api_keys` before persisting; API keys, model list, URL field, and selected model all switch correctly when changing provider
- **Per-provider model selection**: `_selected_model_by_provider` dict tracks last-selected model per provider; persisted in `config.json`; restored on launch and provider switch
- **Readonly dropdowns**: All 5 CTkComboBox set to `state='readonly'` to prevent manual text entry
- **Auto-fetch models**: On app launch and provider switch, models are auto-fetched in background if API keys exist; silent skip when no keys (first use)

## Changes in Phase 4A

- **Model dropdown clear fix**: `_refresh_provider_models()` now clears `model_var` + dropdown display when the selected provider has no cached models
- **Mistral provider**: Added `src/api/mistral_api.py` using OpenAI-compatible endpoint `https://api.mistral.ai/v1`
- **Blackbox provider**: Added `src/api/blackbox_api.py` using OpenAI-compatible endpoint `https://api.blackbox.ai`
- **Provider registration**: Added Mistral + Blackbox to `provider_manager.py` constants, `PROVIDER_BASE_URLS`, `_PROVIDERS`, and `get_metadata()` dispatch

## Changes in Phase 4B

- **Dynamic prompt builder**: Refactored `src/api/prompts.py` from 18 hardcoded prompt strings to 2 builder functions (`_build_gemini_prompt()`, `_build_openai_prompt()`) plus `_PRIORITY_PARAMS`
- **`select_prompt()` extension**: Added `user_hint=""` and `custom_instruction=""` parameters while keeping existing `*_api.py` call sites unchanged (backward-compatible defaults)
- **Title safety net**: Added `_sanitize_title_length()` in `src/api/provider_manager.py` to hard-truncate overlong titles to 200 chars after keyword fill

## Remaining Technical Debt

- **Vision model filtering**: Basic prefix filter applied; no vision-specific detection yet
- **Live-provider validation**: Mistral and Blackbox routing is wired, but real-key verification depends on available API credits

## Pending Phases

- Final integration testing across all providers, merge `dev` → `main`, tag new release

## Last Verified Working

- **Version**: 3.11.3
- **Platform**: Windows
- **Entry point**: `python main.py`
