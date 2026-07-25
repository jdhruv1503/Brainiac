# Brainiac: current-state assessment

_Written July 2026, against commit `c855ce4` (the last commit of the original 2024 project)._

This document is the honest inventory: what the project does today, what is genuinely good
and worth keeping, what is broken, and what can be verified locally. The forward plan lives
in [ROADMAP.md](ROADMAP.md).

---

## 1. What Brainiac is

Brainiac is an agentic pipeline that turns quantitative finance research into backtested
trading signals ("alphas"). Point it at a folder of research PDFs and strategy notes; it
extracts the strategies described in them, asks an LLM to encode each one in WorldQuant's
Fast Expression language, fans each expression out across simulation settings, submits them
to the WorldQuant BRAIN platform for backtesting, and records the results.

```
ResearchPDFs/*.pdf ─┐
                    ├─► LlamaParse ─► distill strategies ─► generate FASTEXPR
Strategies/*.txt   ─┘                                              │
                                                                   ▼
                            SQLite ◄── BRAIN simulation ◄── settings fan-out
```

## 2. Why the idea still holds

The thesis — _the bottleneck in quant research is not compute, it is the rate at which
economic hypotheses get encoded, tested and discarded_ — has aged well. Three things have
changed in the project's favour since 2024:

- **Code-generating models got dramatically better.** In 2024 the pipeline needed
  regex-scraping of JSON out of prose from `WizardLM-2-8x22B`. Today, a small model with a
  constrained-decoding grammar can emit syntactically valid Fast Expression on the first
  attempt, essentially for free.
- **Agentic search patterns matured.** "Propose, evaluate, learn, re-propose" loops
  (AlphaEvolve, FunSearch, and the evolutionary-program-search literature generally) are
  now well-understood. The original README promised "an agentic reinforcement learning
  framework"; the tooling to actually build that now exists off the shelf.
- **Nothing filled the gap.** There is still no good open-source, self-hostable system for
  going from _hypothesis_ to _rigorously evaluated cross-sectional signal_. The adjacent
  tools each solve a different problem: `vectorbt`/`backtesting.py` do single-asset
  strategy backtests, `zipline`/`QuantConnect` do event-driven portfolio simulation,
  `alphalens` scores a factor you already have. None of them own the loop from idea to
  validated signal, and none of them generate candidates.

What has _not_ aged well is the architecture: it is a set of scripts wrapped around a
third-party simulation service, with no local evaluation, no tests, and no way to run it
without that service.

## 3. What the code does today

| Stage | File | What happens |
|---|---|---|
| Watch & schedule | `AlphaGenerator/watchdog.py` | `git pull`, then run the two generators and the sender, every 60 s |
| PDF → markdown | `AlphaGenerator/generate_from_research_pdfs.py` | LlamaParse; result pickled next to the PDF |
| Paper → strategies | `AlphaGenerator/utils/distill_alphas.py` | One LLM call returns a JSON list of `{trading_strategy, description}` |
| Strategy → region | `AlphaGenerator/utils/split_alphas.py` | Tags each strategy with a region |
| Strategy → dataset | `AlphaGenerator/utils/program_alphas.py` | Intended RAG dataset selection — commented out, returns input unchanged |
| Strategy → code | `AlphaGenerator/utils/program_alphas.py` | One LLM call with the operator cheat sheet and field table in context returns `{"code": ...}` |
| Code → neutralisation | `AlphaGenerator/utils/split_alphas.py` | LLM classifies the alpha into a category, mapped to a list of neutralisation settings |
| Fan-out & submit | `AlphaGenerator/send_to_simulation.py` | Cartesian product of universes × neutralisations, POSTed to the local API |
| Simulate | `Simulation/simulate.py` | Round-robins BRAIN credential files, 10 threads per account, polls each simulation to completion |
| Persist | `Simulation/schemas.py` | One wide SQLAlchemy table with every BRAIN in-sample metric and gate check |

## 4. What is genuinely good and must be preserved

It is worth being explicit about this, because the rewrite should not throw it away.

1. **The pipeline decomposition is correct.** parse → distill → encode → select data →
   fan out over settings → simulate → persist is the right factorisation. Each stage has a
   clean input and output. The new architecture keeps exactly these seams.
2. **Per-stage caching to sidecar files is the right instinct.** Writing
   `paper.alphas_init.json`, `paper.code_from_alphas.json` and so on means a crashed run
   resumes rather than re-paying for LLM calls. It needs to become a real content-addressed
   cache, but the idea is sound.
3. **Fanning one idea across universes and neutralisations is real quant practice.** An
   alpha that only survives at `TOP200/SUBINDUSTRY` is a fluke. This is the seed of a
   proper robustness sweep.
4. **The knowledge base is a genuinely valuable asset.** `knowledge/fastexpr_operators.md`
   (113 operators with semantics) and the ten CSV field exports (1,848 distinct fields with
   per-region coverage) are hand-curated and hard to reproduce. They are now the backbone
   of the operator registry and field catalogue.
5. **Capturing the full BRAIN gate-check payload was thorough.** `Simulation/schemas.py`
   records not just Sharpe and fitness but every check's result, limit and value. That is
   the raw material for learning _why_ alphas fail, which is what closes the loop.
6. **Pydantic enums for simulation settings** (`Simulation/schemas.py`) were the right call
   and carry over directly.

## 5. Verified breakages

These were confirmed by running the code in this environment, not by reading it.

- **The persistence layer cannot be imported.** `Simulation/schemas.py:125` calls
  `create_engine('sqlite:///alphas/alpha_results.db')` at module scope, but no `alphas/`
  directory exists or is created. `import schemas` raises
  `sqlalchemy.exc.OperationalError: unable to open database file`. Since `main.py` and
  `simulate.py` both import it, **the simulation service cannot start from a fresh clone.**
- **A function is called that does not exist.** `sql_write_failed_alpha(row)` at
  `Simulation/simulate.py:145` has no definition anywhere in the repository. Every failed
  simulation raises `NameError`.
- **A referenced knowledge file was never committed.** `program_alphas.py:29` and `:112`
  read `datasets_usa.md`. It does not exist. Any alpha with `region == "USA"` raises
  `FileNotFoundError` — which is moot only because `split_alphas_region` hardcodes `CHN`.
- **`requirements.txt` cannot install a working environment.** It omits `openai`,
  `llama-index-llms-groq`, `llama-index-llms-deepinfra` and `pydantic`, all of which are
  imported, and lists `asyncio`, which is a standard-library module. Nothing is pinned.

## 6. Bug and debt inventory

### Correctness — will raise or corrupt data

| # | Location | Issue |
|---|---|---|
| 1 | `Simulation/schemas.py:125` | Engine created at import time against a non-existent directory |
| 2 | `Simulation/simulate.py:145` | `sql_write_failed_alpha` undefined |
| 3 | `Simulation/simulate.py:442-446` | `print(r)` and `DBSession.add(alpha_result)` sit outside the `if/else`, so the failure path dereferences an unbound `alpha_result` |
| 4 | `Simulation/simulate.py:22-34` | `new_get`/`new_post` retry by unbounded recursion inside a bare `except:` — a persistent network fault becomes `RecursionError`, and `KeyboardInterrupt` is swallowed |
| 5 | `Simulation/simulate.py:455` | Logs to `logging/log.log`; the directory is never created |
| 6 | `Simulation/simulate.py:463-466` | `executor.map(...)` result is never consumed, so every worker exception is silently discarded |
| 7 | `Simulation/simulate.py:445` | One module-global `DBSession` shared across 10 threads; SQLAlchemy sessions are not thread-safe |
| 8 | `Simulation/main.py:27` | `chunk_into_n(data, len(sessions))` divides by zero when no credential file is present |
| 9 | `Simulation/simulate.py:46,52` | `input()` on the login path blocks forever under `uvicorn` |
| 10 | `AlphaGenerator/utils/program_alphas.py:27-29` | Windows path separators (`utils\\BrainKnowledgebaseSyntax\\...`) break on Linux and macOS |
| 11 | `AlphaGenerator/utils/split_alphas.py:74-83` | `prune_datasets` mutates `alp` and returns the always-empty `new_alphas` |
| 12 | `generate_from_research_pdfs.py:107`, `send_to_simulation.py:60` | Alphas serialised with `str(obj).replace("'", '"')`, which corrupts any description containing an apostrophe; re-read with a hardcoded `cp1252` codec |
| 13 | `send_to_simulation.py:24` | `alpha not in done_alphas` compares a line against a list of differently-terminated lines, so dedupe never fires |
| 14 | `send_to_simulation.py:65` | `alphas.jsonl` is deleted after a successful POST, destroying the audit trail |

### Design and architecture

| # | Location | Issue |
|---|---|---|
| 15 | `Simulation/main.py:30-34` | `simulate_all` calls each blocking `session.simulate(chunk)` in sequence, so accounts run one after another rather than concurrently — and it does so inside a `BackgroundTask`, blocking the event loop |
| 16 | `Simulation/main.py` | No authentication; anything that can reach port 8000 can queue simulations against your account |
| 17 | `Simulation/simulate.py:73-99` | `while True: post(...)` with no backoff, jitter or attempt cap |
| 18 | `Simulation/creds/*.json` | Plaintext credentials on disk, and the README instructs users to create several |
| 19 | `utils/program_alphas.py:79-97` | The "RAG dataset retrieval" advertised in the README is commented out; the function returns its input |
| 20 | `utils/split_alphas.py:109-119` | `split_alphas_region` hardcodes `CHN`; the USA branch is commented out, making the "Integration of USA datasets" roadmap item unreachable |
| 21 | everywhere | No feedback path from simulation results back into generation, so the promised "continuous learning / reinforcement learning framework" does not exist |
| 22 | `AlphaGenerator/watchdog.py:12` | `git pull` every 60 s as a deployment mechanism |
| 23 | `AlphaGenerator/watchdog.py` | Module shadows the PyPI `watchdog` package it sounds like it uses |
| 24 | — | No local evaluation, so the only feedback signal costs a multi-minute remote round trip |

### Modernisation

| # | Issue |
|---|---|
| 25 | Models `WizardLM-2-8x22B`, `Mixtral-8x22B-Instruct-v0.1` and `Mistral-7B-Instruct-v0.3` are early-2024 vintage and effectively retired; `response_format={"type":"json_object"}` combined with `tool_choice="auto"` is no longer a valid combination on most providers |
| 26 | `distill_alphas.py:14` reads `DEEPINFRA_API_KEYS` into a variable named `GroqAPIKeys`, and imports `llama_index.llms.groq` / `DeepInfraLLM` without using either; module-scope `os.environ[...]` means any import fails without keys |
| 27 | `split_alphas.py:23` — `map = {...}` shadows the builtin |
| 28 | `schemas.py:48` — `sqlalchemy.ext.declarative.declarative_base` is deprecated in SQLAlchemy 2.0 |
| 29 | No tests, no CI, no linting, no type checking, no formatter, no packaging, no Dockerfile, no lockfile |
| 30 | Single hardcoded 60-second poll loop instead of a job queue with retries and idempotency |
| 31 | Bare `except:` in 11 places, swallowing `KeyboardInterrupt` and `SystemExit` |

### Legal and ethical — blocks commercialisation

| # | Issue |
|---|---|
| 32 | The multi-credential rotation in `Simulation/main.py:14-16` exists specifically to exceed BRAIN's per-account concurrency limit. This is a terms-of-service problem, and no product can ship it. It must become honest single-account rate limiting, with BRAIN as one optional backend rather than the only one |
| 33 | Alphas submitted to BRAIN carry platform IP entanglement. The sellable asset is the research tooling, not the alphas |
| 34 | No licence file, no contribution guide, no security policy |

## 7. What can be tested in this environment

Verified during this session.

| Capability | Testable? | Evidence |
|---|---|---|
| Fast Expression lexer/parser/printer | **Yes** | Round-tripped 8 representative alphas including multi-statement, ternary, named-argument and comparison forms |
| Operator registry | **Yes** | 163 operators registered from the bundled cheat sheet |
| Field catalogue | **Yes** | 2,542 field/delay rows, 1,848 distinct fields, 10 datasets loaded from the CSV exports |
| Validator / linter | **Yes** | Correctly flagged unknown field (`clos` → suggests `close`), bad arity, non-literal window, non-group grouping argument, unknown operator (`rnk` → suggests `rank`), unknown keyword, region-unavailable field, constant alpha, literal division by zero |
| Local evaluation and backtesting | **Yes** | numpy 2.5.1, pandas 3.0.5 available; benchmark below |
| Service layer (FastAPI, SQLAlchemy, Alembic) | **Yes** | `TestClient` round trip works; SQLAlchemy 2.0.51, Alembic installed |
| Local PDF text extraction | **Yes** | PyMuPDF read all 46 pages / 102,791 characters of the bundled SSRN paper. **LlamaParse is therefore not a hard dependency** |
| Outbound network | **Yes** | `arxiv.org` 200, `pypi.org` 200, `api.worldquantbrain.com` 401 (live, needs auth), `papers.ssrn.com` 403 (bot-blocked — see roadmap note on paper sources) |
| LLM generation | **No** | No `DEEPINFRA_API_KEYS` / `OPENAI_API_KEY` injected. Mitigation: a recorded-fixture transport plus a deterministic fake provider, so the pipeline is testable without keys |
| LlamaParse | **No** | No key. Mitigation: PyMuPDF is the default; LlamaParse becomes an optional accuracy upgrade |
| BRAIN simulation | **No** | No credentials. Mitigation: cassette-style recorded responses for client tests, plus a `--network` pytest marker for live runs |

## 8. The benchmark that justifies the whole plan

The single most important number for this project is _how many candidate alphas can be
evaluated per hour_, because search quality scales with it. Measured here, single-core
numpy, on a representative alpha (`rank(-ts_delta(close, 5) / ts_mean(volume, 20))`):

| Panel | Per alpha | Throughput |
|---|---|---|
| TOP500 × 5 years (research panel) | 26 ms | **138,000 alphas/hour/core** |
| TOP3000 × 10 years (full panel) | 349 ms | **10,300 alphas/hour/core** |
| BRAIN, one account (3 concurrent, ~1–3 min each) | ~60–120 s | **~90–180 alphas/hour** |

Local evaluation is **three orders of magnitude** faster than the remote loop on a research
panel, needs no account, costs nothing, and works offline. Roughly 40% of the time is the
double-`argsort` in `rank`, which is the obvious first optimisation target, and shared
subtrees across a population are cacheable on top of that.

This is the reframe in a single table: BRAIN should be the _confirmation_ step for the
handful of alphas that survive local search, not the search loop itself.
