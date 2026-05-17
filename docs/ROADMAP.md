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
