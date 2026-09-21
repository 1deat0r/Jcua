# Changelog

## 0.1.1 — 2026-09-21
- Jev guard #1 (default OFF): choice-over-criteria schema, fail-safe escalate, floor 0.75. Live probe harmless APPROVE 1.0 / dangerous ESCALATE 1.0; `run` blocks unless `--force`.
- Library registry + retriever (retrieve-or-create, threshold 0.46) + traces/trace.jsonl + library.db stats.
- `jcua library audit` file/DB check; 3 golden tasks with `golden_gate()`.
- Proof: seed reuse `reused:true`, audit `pass`, golden `3/3`.

## 0.1.0 — 2026-09-21
- Skeleton: CLI, Computer abstraction, single Jev transport, 4 platform targets, golden stub, upstream sync script.
