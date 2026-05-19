# Current State — RJ Auto Metadata

> Snapshot at Phase 4B.5 completion.

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

## Changes in Phase 4B.5

- **Stop mechanism refactored**: Created `src/utils/stop_flag.py` as single source of truth for the global stop flag
- **Per-module flags removed**: Removed `FORCE_STOP_FLAG` / `_force_stop`, `set_force_stop()`, `reset_force_stop()`, `is_stop_requested()` from all 7 `*_api.py` files
- **Centralized import**: Each `*_api.py` now imports `is_stop_requested` from `stop_flag`; `check_stop_event()` kept per-module (uses `stop_event` threading.Event)
- **provider_manager delegation**: `set_force_stop()`, `reset_force_stop()`, `is_stop_requested()` now delegate directly to `stop_flag` module
- **Infrastructure imports**: `compression.py` and `exif_writer.py` import `is_stop_requested` from `stop_flag` instead of `gemini_api`
- **UI stop imports**: All `app.py` imports of `set_force_stop`/`reset_force_stop` from `gemini_api` replaced with `stop_flag` imports
- **Premature UI reset fix**: `_check_thread_ended()` timeout increased from 2.5s to 30s
- **Separated UI reset from stop flag reset**: Added `_reset_ui_buttons_only()` — resets UI without clearing stop flag; `reset_force_stop()`/`stop_event.clear()` only called when thread is confirmed dead

## Changes in Phase 4C (UI Tab Settings)

- **Section headers removed**: Removed "Folder Input/Output" header+tooltip, "Settings and API Keys" header+tooltip, and "Logs" label from the UI to reclaim vertical space
- **Settings tabview**: Replaced `settings_row` CTkFrame with `CTkTabview` containing "Settings" and "Advanced" tabs
- **Settings tab**: Existing 3×3 settings grid (Keywords/Workers/Delay, Theme/Quality/Embed, Rename/Category/Foldering) moved into "Settings" tab unchanged
- **Advanced tab**: Blank placeholder tab added with "coming soon" label for future prompt customization
- **Window size**: Default geometry reduced from 600×800 to 600×700

## Changes in Phase 4C Step 2 (Advanced Tab Content)

- **Advanced tab layout**: Replaced placeholder with Option B 3-column layout:
  - Col 0: Instructions textarea (CTkTextbox, full height via rowspan, stretches horizontally)
  - Col 1: Hint entry + Inject Keywords entry (sub-frame matching Settings tab style)
  - Col 2: Title min/max + Desc min/max limit entries (compact sub-frames)
- **New StringVars**: Added 7 variables — `hint_var`, `custom_instruction_var`, `inject_keywords_var`, `title_min_words_var`, `title_max_chars_var`, `desc_min_words_var`, `desc_max_chars_var`
- **Config persistence**: All 7 new vars saved/loaded in `_save_settings()`/`_load_settings()` with sensible Detailed-preset defaults
- **No backend wiring**: Values are UI-only; passing to `batch_processing` is Phase 4C Step 3

## Remaining Technical Debt

- **Vision model filtering**: Basic prefix filter applied; no vision-specific detection yet
- **Live-provider validation**: Mistral and Blackbox routing is wired, but real-key verification depends on available API credits

## Pending Phases

- Phase 4C Step 3: Wire Advanced tab values to batch_processing dispatch
- Final integration testing across all providers, merge `dev` → `main`, tag new release

## Last Verified Working

- **Version**: 3.11.3
- **Platform**: Windows
- **Entry point**: `python main.py`
