# Current State — RJ Auto Metadata

> Snapshot at Phase 0 completion.

## Version

**3.11.3** (tagged `v3.11.3` on `main`)

## Branch Structure

- `main` — stable release baseline (v3.11.3)
- `dev` — integration branch (created in Phase 0)
- `task/docs-governance` — Phase 0 work branch

## Supported Providers

| Provider | Current Endpoint Type | Status |
|---|---|---|
| **Gemini** | Native REST (`generateContent`) | To be migrated to OpenAI compat |
| **OpenAI** | Responses API (`/v1/responses`) | Staying as Responses API |
| **OpenRouter** | Chat Completions | No change planned |
| **Groq** | Chat Completions | No change planned |
| **KoboiLLM** | Chat Completions | No change planned |

## Known Technical Debt

- **Hardcoded model presets**: ~50+ model IDs spread across all 5 `*_api.py` files (`GEMINI_MODELS`, `OPENAI_MODEL_PRESETS`, `OPENROUTER_MODEL_PRESETS`, `GROQ_MODEL_PRESETS`, `KOBOILLM_MODEL_PRESETS`)
- **Gemini native REST**: Only provider not using OpenAI-compatible endpoint; requires separate SDK/REST dual path (~770 lines in `gemini_api.py`)
- **Duplicate `_clean_json_text()`**: Identical function copied in `openrouter_api.py`, `koboillm_api.py`, and `openai_api.py`
- **Gemini Auto Rotation**: Model rotation logic (`select_next_model`, `wait_for_model_cooldown`, `MODEL_LOCK`) — to be removed
- **Dead code**: `calculate_smart_delay()`, `DEBUG_FORCE_FAILURE`, commented-out debug blocks in `groq_api.py`, `openrouter_api.py`, `openai_api.py`
- **Noisy terminal output**: All log severity levels printed to terminal; no filter for warning/error only
- **Duplicate `gpt-4o`**: Appears twice in `_STRUCTURED_OUTPUT_MODEL_PREFIXES` in `openai_api.py`

## UI Current State

- **Save/Load/Delete buttons**: Exist for API key file management — to be replaced (Save → Fetch, Load/Delete removed)
- **Auto Retry toggle**: Exists as UI switch — to be removed (hardcoded `True` in backend)
- **Model dropdown**: Populated from hardcoded presets — to be replaced with dynamic fetch
- **Provider dropdown**: Located in `api_paid_frame` — to be moved up in layout
- **Custom provider**: Not yet supported — to be added as 6th option

## Pending Phases

- **Phase 1**: Backend refactor (`task/refactor-backend`) — items B1–B9, U1–U2
- **Phase 2**: UI refactor (`task/refactor-ui`) — items UI1–UI11

## Last Verified Working

- **Version**: 3.11.3
- **Platform**: Windows
- **Entry point**: `python main.py`
