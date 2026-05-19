# Roadmap — RJ Auto Metadata v4 Refactor

## Phase 0: Docs Governance — Complete

- Updated `.gitignore` for build artifacts, release archives, logs, API keys, env files
- Created `dev` branch from `main`
- Created `AGENTS.md` at repository root
- Created `docs/ARCHITECTURE.md`, `docs/GIT_POLICY.md`, `docs/CURRENT_STATE.md`, `docs/HANDOFF.md`, `docs/ROADMAP.md`

## Phase 1: Backend Refactor (`task/refactor-backend`) — Complete

| # | Item | Status |
|---|---|---|
| B1 | Gemini → OpenAI compat | ✅ Done — ~470 lines removed, OpenAI SDK with `v1beta/openai/` |
| B2 | Dead code cleanup | ✅ Done — removed debug blocks from 3 files |
| B3 | Remove hardcoded model presets | ✅ Done — removed from all 5 API files |
| B4 | Centralize `_clean_json_text()` | ✅ Done — moved to `src/utils/json_utils.py` |
| B5 | Remove Gemini Auto Rotation | ✅ Done — part of B1 |
| B6 | Add `PROVIDER_BASE_URLS` | ✅ Done — added to `provider_manager.py` |
| B7 | Add Custom provider handler | ✅ Done — dispatches via openrouter handler |
| B8 | Refactor dispatch chain | ✅ Done — added `base_url_override`, guarded `None` modules |
| B9 | Fix duplicate `gpt-4o` | ✅ Done |
| U1 | Terminal log severity filter | ✅ Done — `_TERMINAL_PRINT_TAGS` in `logging.py` |
| U2 | Create `json_utils.py` | ✅ Done |

## Phase 2: UI Refactor (`task/refactor-ui`) — Complete

| # | Item | Status |
|---|---|---|
| UI-1 | Remove Load + Delete buttons and dead methods | ✅ Done |
| UI-2 | Hardcode auto_retry=True, remove Auto Retry switch | ✅ Done |
| UI-3 | Save → Fetch button, threaded `_fetch_models()` | ✅ Done |
| UI-4 | Add Base URL field (visible only for Custom) | ✅ Done |
| UI-5 | Per-provider model state (`_models_by_provider`) | ✅ Done |
| UI-6 | Add "Custom" to provider dropdown | ✅ Done |
| UI-7 | Persist `models_by_provider` + `custom_base_url` in config | ✅ Done |

Note: `fetch_models()` in `provider_manager.py` is a stub returning `[]`. Real API fetch deferred to Phase 3.

## Phase 3: Integration & Release — Complete

| # | Item | Status |
|---|---|---|
| P3-1 | Implement `fetch_models()` with OpenAI SDK | ✅ Done |
| P3-2 | Vendor CTkScrollableDropdown, attach to all 5 dropdowns | ✅ Done |
| P3-3 | Pass `command` callbacks through scrollable dropdowns | ✅ Done |
| P3-4 | Per-provider API key sync on provider switch | ✅ Done |
| P3-5 | Per-provider model selection persistence | ✅ Done |
| P3-6 | Readonly dropdowns (`state='readonly'`) | ✅ Done |
| P3-7 | Auto-fetch models on startup and provider switch | ✅ Done |

Remaining: merge `dev` → `main`, tag next version.

## Phase 4A: Provider Expansion & UI Fix (`task/add-providers`) — Complete

| # | Item | Status |
|---|---|---|
| P4A-1 | Fix model dropdown clear when cache is empty | ✅ Done |
| P4A-2 | Add `src/api/mistral_api.py` | ✅ Done |
| P4A-3 | Add `src/api/blackbox_api.py` | ✅ Done |
| P4A-4 | Register both providers in `provider_manager.py` | ✅ Done |
| P4A-5 | Update docs (`CURRENT_STATE`, `HANDOFF`, `ROADMAP`) | ✅ Done |

Notes:
- Mistral and Blackbox use OpenAI-compatible routing via configured base URLs.
- Live key/credit validation is deferred to provider-backed testing.

## Phase 4B: Dynamic Prompt Builder (`task/dynamic-prompt-builder`) — Complete

| # | Item | Status |
|---|---|---|
| P4B-1 | Replace 18 hardcoded prompt strings with dynamic builders in `src/api/prompts.py` | ✅ Done |
| P4B-2 | Add `_PRIORITY_PARAMS` map (`Detailed`/`Balanced`/`Fast`) | ✅ Done |
| P4B-3 | Extend `select_prompt()` with `user_hint` + `custom_instruction` defaults | ✅ Done |
| P4B-4 | Add title hard-truncation safety net in `src/api/provider_manager.py` | ✅ Done |
| P4B-5 | Update docs (`CURRENT_STATE`, `HANDOFF`, `ROADMAP`) | ✅ Done |

Notes:
- No UI changes in Phase 4B; new prompt inputs are backend-ready and will be wired in Phase 4C.

## Phase 4B.5: Stop Mechanism Fix (`task/fix-stop-mechanism`) — Complete

| # | Item | Status |
|---|---|---|
| P4B5-1 | Create `src/utils/stop_flag.py` as single global stop flag | ✅ Done |
| P4B5-2 | Remove per-module stop flags from all 7 `*_api.py` files | ✅ Done |
| P4B5-3 | Update `provider_manager.py` to delegate to `stop_flag` | ✅ Done |
| P4B5-4 | Fix premature UI reset timeout (2.5s → 30s) in `_check_thread_ended()` | ✅ Done |
| P4B5-5 | Separate UI reset from stop flag reset (`_reset_ui_buttons_only()`) | ✅ Done |
| P4B5-6 | Replace all `gemini_api` stop imports in `app.py` with `stop_flag` | ✅ Done |
| P4B5-7 | Update `compression.py` and `exif_writer.py` imports | ✅ Done |
| P4B5-8 | Update docs (`CURRENT_STATE`, `HANDOFF`, `ROADMAP`) | ✅ Done |

## Phase 4C: UI Tab Settings (`task/ui-tab-settings`) — Complete

| # | Item | Status |
|---|---|---|
| P4C-1 | Remove "Folder Input/Output" section header + tooltip | ✅ Done |
| P4C-2 | Remove "Settings and API Keys" section header + tooltip | ✅ Done |
| P4C-3 | Remove "Logs" label, promote log textbox to row=0 | ✅ Done |
| P4C-4 | Replace `settings_row` with `CTkTabview` (Settings + Advanced) | ✅ Done |
| P4C-5 | Reparent 3 settings columns into Settings tab | ✅ Done |
| P4C-6 | Add blank Advanced tab with placeholder label | ✅ Done |
| P4C-7 | Update docs (`CURRENT_STATE`, `HANDOFF`, `ROADMAP`) | ✅ Done |

## Out of Scope

- No new providers beyond Custom
- No UI theme changes
- No new file format support
- No changes to ExifTool integration or CSV export logic
