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

## Phase 3 Status: Complete

### What Was Done

- **fetch_models()**: Replaced stub with real implementation using OpenAI SDK `client.models.list()` endpoint; resolves base URL from `PROVIDER_BASE_URLS` for built-in providers or user-supplied URL for Custom; filters non-generative model IDs via `_SKIP_PREFIXES`
- **CTkScrollableDropdown**: Vendored Akascape/CTkScrollableDropdown (MIT) into `src/ui/CTkScrollableDropdown/`; attached to all 5 CTkComboBox dropdowns for scrollable popup behavior; `command` callbacks passed through for provider and theme
- **Per-provider key sync**: `_on_provider_change` now syncs textbox before persisting; API keys, model list, URL, and selected model all switch correctly on provider change
- **Per-provider model selection**: `_selected_model_by_provider` dict persisted in `config.json`; model restored on launch and provider switch
- **Readonly dropdowns**: All 5 CTkComboBox set to `state='readonly'`
- **Auto-fetch models**: `_auto_fetch_models()` runs on startup (500ms delay) and on provider switch; silently skips if no keys

### What Is NOT Done / Deferred

- Vision-specific model detection not implemented (basic prefix filter only)

## Phase 4A Status: Complete

### What Was Done

- **UI bug fix**: `_refresh_provider_models()` now clears the model display (`model_var` + dropdown text) when selected provider has no cached models
- **Provider add**: Created `src/api/mistral_api.py` (OpenAI-compatible, base URL `https://api.mistral.ai/v1`, public entry `get_mistral_metadata`)
- **Provider add**: Created `src/api/blackbox_api.py` (OpenAI-compatible, base URL `https://api.blackbox.ai`, public entry `get_blackbox_metadata`)
- **Provider registry**: Updated `src/api/provider_manager.py` with `PROVIDER_MISTRAL` and `PROVIDER_BLACKBOX` constants, added both to `PROVIDER_BASE_URLS`, `_PROVIDERS`, and `get_metadata()` dispatch routing

## Phase 4B Status: Complete

### What Was Done

- **Prompt refactor**: Replaced 18 hardcoded prompt string variants in `src/api/prompts.py` with dynamic builders (`_build_gemini_prompt()`, rewritten `_build_openai_prompt()`) and `_PRIORITY_PARAMS`
- **Prompt entry point update**: Extended `select_prompt()` signature with `user_hint=""` and `custom_instruction=""` while preserving existing `*_api.py` call compatibility
- **Provider safety guard**: Added `_sanitize_title_length()` in `src/api/provider_manager.py` and chained it after `_fill_keywords_if_short()` for all provider return paths

### Notes for Next Phase (4C)

- No UI changes in Phase 4B; `user_hint` and `custom_instruction` are wired at API prompt builder level but currently always empty (`""`) from existing UI flows
- Groundwork is ready for Phase 4C UI additions: Image Hint field, Custom Instructions field, Specific Keywords support, and Custom Quality settings

### Validation Notes

- Import and provider-list checks pass (`provider_manager.list_providers()` includes Mistral and Blackbox)
- UI launch/routing confirmed against provider docs and configured base URLs
- Real API-key execution for Mistral and Blackbox not validated due unavailable key credits in this session

## Phase 4B.5 Status: Complete

### What Was Done

- **Stop flag centralization**: Created `src/utils/stop_flag.py` as single source of truth for global stop flag (`_FORCE_STOP` bool with `is_stop_requested()`, `set_force_stop()`, `reset_force_stop()`)
- **Per-module flag removal**: Removed `FORCE_STOP_FLAG`/`_force_stop`, `set_force_stop()`, `reset_force_stop()`, `is_stop_requested()` from all 7 `*_api.py` files (gemini, openai, openrouter, groq, koboillm, mistral, blackbox)
- **Import update**: Each `*_api.py` now imports `is_stop_requested` from `stop_flag`; `check_stop_event()` kept in each module (uses threading.Event)
- **provider_manager simplification**: `set_force_stop()`, `reset_force_stop()`, `is_stop_requested()` now delegate to `stop_flag` directly instead of iterating all provider modules
- **Infrastructure import fix**: `compression.py` and `exif_writer.py` import `is_stop_requested` from `stop_flag` instead of `gemini_api`
- **app.py stop import fix**: All `gemini_api` stop imports replaced with `stop_flag` imports
- **Premature UI reset fix**: `_check_thread_ended()` timeout increased from 2.5s to 30s
- **UI/stop separation**: Added `_reset_ui_buttons_only()` — resets UI controls without clearing stop flag; `reset_force_stop()`/`stop_event.clear()` only happen when thread is confirmed dead

### Bug Fixed

The original stop mechanism had two bugs:
1. Each provider had its own independent stop flag — stopping one didn't affect others
2. `_check_thread_ended()` had a 2.5s timeout that reset the stop flag while threads were still alive, causing them to continue after the user clicked Stop

Both are now resolved by the single centralized flag and the separated UI/stop-state reset.

## Phase 4C Status: Complete (UI Tab Settings)

### What Was Done

- **Section header removal**: Removed "Folder Input/Output" header (tooltip + `_create_header_with_help` call + `.grid()`), "Settings and API Keys" header (same pattern), and "Logs" `CTkLabel` from `_create_log_frame()`
- **Log frame adjustment**: `log_text` promoted to row=0, `grid_rowconfigure` updated accordingly
- **Settings tabview**: Replaced `settings_row` CTkFrame with `self.settings_tabview` (`CTkTabview`) containing "Settings" and "Advanced" tabs
- **Reparenting**: Three settings column frames (`settings_col1`, `settings_col2`, `settings_col3`) reparented from `settings_row` to `settings_tabview.tab("Settings")`
- **Advanced tab placeholder**: Added "Advanced prompt settings — coming soon." label
- **Window size**: Default geometry reduced from 600×800 to 600×700

### Notes for Next Phase

- The `_create_header_with_help()` method itself was intentionally kept — only the two calls and their tooltip strings were removed
- The Advanced tab is ready for Phase 4C content: Image Hint field, Custom Instructions field, Specific Keywords, Custom Quality

## Next Phase

Phase 4C content (UI wiring for new prompt inputs into the Advanced tab), then final integration testing across all providers before merge `dev` → `main` and release tag.

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
| CTkScrollableDropdown | Vendored (MIT); replaces native CTkComboBox popup |
| fetch_models() | OpenAI SDK `client.models.list()` with prefix filter |

## Important Files

1. `AGENTS.md`
2. `docs/CURRENT_STATE.md`
3. `docs/ARCHITECTURE.md`
4. `src/ui/CTkScrollableDropdown/` — vendored scrollable dropdown widget
5. `src/api/provider_manager.py` — fetch_models() implementation
