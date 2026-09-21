# Changelog

## Unreleased (0.1.5 fill-decider)
- `fill.py` planner + `jcua fill [--s1]`: heuristic fallback everywhere, S1-live 3/3 on fixture.

## 0.1.4 — 2026-09-21
- Sandboxed jcua-vs-cua offline benchmark (Docker, no network/keys): docs/BENCH.md + evals/bench harness.

## 0.1.3 — 2026-09-21
- Vendored `demo.jsonl` (196 real rows) + torch-optional scorer + `eval --s1`.
- `golden/` skips METRIC tasks; retrieval gate unchanged.
## 0.1.2 — 2026-09-21
- `evolve --once` dry-run preview + `--apply` promotion (`uses>=3 sr>=0.8 value>=median` + golden gate).
- Live: hello-jcua promoted candidate→default, audit pass, golden 3/3.
## 0.1.1 — 2026-09-21
- Jev guard #1 (default OFF): choice-over-criteria schema, fail-safe escalate, floor 0.75. Live probe harmless APPROVE 1.0 / dangerous ESCALATE 1.0; `run` blocks unless `--force`.
- Library registry + retriever (retrieve-or-create, threshold 0.46) + traces/trace.jsonl + library.db stats.
- `jcua library audit` file/DB check; 3 golden tasks with `golden_gate()`.
- Proof: seed reuse `reused:true`, audit `pass`, golden `3/3`.

## 0.1.0 — 2026-09-21
- Skeleton: CLI, Computer abstraction, single Jev transport, 4 platform targets, golden stub, upstream sync script.
