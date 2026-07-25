# AGENTS.md

## Cursor Cloud specific instructions

Brainiac is a single Python project (Python 3.12) with two parts:

- **Simulation API** (`Simulation/`) — the core local service. FastAPI + SQLite.
- **AlphaGenerator** (`AlphaGenerator/`) — an LLM worker that generates alphas and POSTs them to the Simulation API. Requires external API keys, so it cannot run end-to-end without secrets (see below).

Setup instructions live in `README.md`. Notes below are the non-obvious gotchas.

### Python environment

- Dependencies are installed into a virtualenv at `.venv` (gitignored). Use `.venv/bin/python` (there is no auto-activation).
- `requirements.txt` is **incomplete**: `openai`, `llama-index-llms-groq`, and `llama-index-llms-deepinfra` are imported by `AlphaGenerator/utils/*` but not listed. The startup update script installs them alongside `requirements.txt`. `pydantic` is pulled in transitively via `fastapi`.
- The `asyncio` line in `requirements.txt` installs a harmless no-op stub on Python 3.12 — `import asyncio` still resolves to the stdlib.
- There is a `tenacity` version conflict (`llama-index-llms-deepinfra` wants `<8.4.0`, `llama-cloud-services` wants `>=8.5.0`). Pinning `tenacity>=8.5.0,<10` works at runtime for both; `pip check` will still print a metadata warning that can be ignored.

### Running the Simulation API (core service)

- Run from the `Simulation/` directory (it uses relative paths): `cd Simulation && /workspace/.venv/bin/python main.py` → serves on `http://0.0.0.0:8000`. Swagger UI at `/docs`.
- The `Simulation/alphas/` directory must exist before import (the SQLite engine is created at import time) and `Simulation/logging/` is used for logs. These are gitignored/empty, so the update script `mkdir -p`s them.
- The API starts with zero WorldQuant credentials (`sessions == []`). `GET /` and `POST /add_alphas` work and return 200, but the background `simulate_all` task raises `ZeroDivisionError` when there are no sessions. To actually run backtests, add real WorldQuant BRAIN accounts as `Simulation/creds/<name>.json` (`{"email","password"}`); `example.json` is ignored. First BRAIN login may block on an interactive `input()` biometric prompt.

### Running the AlphaGenerator worker

- Run from `AlphaGenerator/`. Requires env vars `LLAMA_PARSE_API_KEYS` and `DEEPINFRA_API_KEYS` (comma-separated), which are read at **import time** — modules raise `KeyError` on import if unset. Also needs network access to LlamaParse / DeepInfra. It cannot run end-to-end in the cloud without these secrets.

### Lint / test / build

- There is no test suite, linter config, or build step. Use `python -m py_compile` on the `.py` files as a syntax check.
