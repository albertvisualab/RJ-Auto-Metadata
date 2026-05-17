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

## Out of Scope

- No new providers beyond Custom
- No UI theme changes
- No new file format support
- No changes to ExifTool integration or CSV export logic
