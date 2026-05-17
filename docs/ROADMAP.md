# Roadmap — RJ Auto Metadata v4 Refactor

## Phase 0: Docs Governance — Complete

- Updated `.gitignore` for build artifacts, release archives, logs, API keys, env files
- Created `dev` branch from `main`
- Created `AGENTS.md` at repository root
- Created `docs/ARCHITECTURE.md`, `docs/GIT_POLICY.md`, `docs/CURRENT_STATE.md`, `docs/HANDOFF.md`, `docs/ROADMAP.md`

## Phase 1: Backend Refactor (`task/refactor-backend`)

| # | Item | Description |
|---|---|---|
| B1 | Gemini → OpenAI compat | Biggest change — migrate from native REST to `v1beta/openai/` endpoint, ~600 lines removed |
| B2 | OpenAI dead code cleanup | Keep Responses API, remove unused parsers and debug artifacts |
| B3 | Remove hardcoded model presets | Delete all `*_MODEL_PRESETS` dicts and `DEFAULT_MODEL` constants from 5 API files |
| B4 | Centralize `_clean_json_text()` | Move duplicate function to `src/utils/json_utils.py` |
| B5 | Remove Gemini Auto Rotation | Delete model lock, cooldown, `select_next_model`, etc. (part of B1) |
| B6 | Add `PROVIDER_BASE_URLS` | Add base URL mapping constant to `provider_manager.py` |
| B7 | Add Custom provider handler | Handle `"Custom"` provider in dispatch with user-defined base URL |
| B8 | Refactor dispatch chain | Replace if-elif chain with uniform `module.get_metadata(...)` interface |
| B9 | Fix duplicate `gpt-4o` | Remove duplicate entry in `_STRUCTURED_OUTPUT_MODEL_PREFIXES` |
| U1 | Terminal log severity filter | Add `_TERMINAL_PRINT_TAGS` filter in `src/utils/logging.py` |
| U2 | Create `json_utils.py` | New shared utility at `src/utils/json_utils.py` |

## Phase 2: UI Refactor (`task/refactor-ui`)

- Remove Load + Delete buttons and their backend functions (`_load_api_keys`, `_save_api_keys`, `_delete_selected_api_key`)
- Remove Auto Retry switch, hardcode `True` in `_run_processing()`
- Replace Save button → Fetch button (dynamic model fetch via `GET /v1/models`)
- Restructure layout: Provider and Model dropdowns moved up into API section
- Add Custom URL field (disabled for built-in providers, enabled for Custom)
- Implement per-provider model state (`models_by_provider`, `selected_model_by_provider`) with restore on provider switch
- Add `"Custom"` to provider dropdown list

## Phase 3: Integration & Release

- Final integration testing across all providers
- Cleanup and polish
- Merge `dev` → `main` as new release
- Tag as next version

## Out of Scope

- No new providers beyond Custom
- No UI theme changes
- No new file format support
- No changes to ExifTool integration or CSV export logic
