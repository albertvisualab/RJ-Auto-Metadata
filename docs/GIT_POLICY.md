# Git Policy — RJ Auto Metadata

## Branch Model

```
main              ← stable releases only
dev               ← integration branch, always deployable
task/<name>       ← feature/fix/refactor branches, branched from dev
```

### Branch Naming Conventions

- `task/docs-governance` — documentation and governance setup
- `task/refactor-backend` — backend code refactoring
- `task/refactor-ui` — UI code refactoring
- `task/refactor-backend-openai-compat` — specific sub-task example
- `task/refactor-ui-dynamic-models` — specific sub-task example

## Commit Message Format

### Structure

```
<type>(<scope>): <description>

<body>
```

- **Subject line**: max 72 characters
- **Types**: `feat`, `fix`, `refactor`, `docs`, `chore`, `style`, `test`
- **Blank line** between subject and body
- **Body** explains WHY, not WHAT

### Example

```
refactor(gemini): migrate to openai-compat endpoint

Remove SDK/REST dual-path (~600 lines). Standardize on OpenAI
SDK with v1beta/openai/ base URL. Eliminates auto-rotation logic
and complex thinking config handling.
```

## Merge Policy

1. Task branch → `dev` (squash merge if commit history is noisy)
2. `dev` → `main` only for releases
3. Never commit directly to `main` or `dev`

## Push Policy

- **Agents must not push.** Only the human user pushes to remote.
- All agent work stays local until the human explicitly pushes.

## Forbidden Committed Files

The following must never be committed to any branch:

- API keys or secrets
- `.env`, `*.env`, `.env.*` files
- `api_jikaperlu/` directory
- `dist_nuitka/`, `dist/`, `build/` directories
- `*.zip`, `*.exe`, `*.dmg` release artifacts
- `v*/` release folders
- `logs` file
- `__pycache__/`, `*.pyc`, `*.pyo` bytecode

All of these are covered by `.gitignore`.

## Tagging

- Releases are tagged on `main` as `v3.x.x` (e.g., `v3.11.3`)
- Tags are created only by the human user at release time
