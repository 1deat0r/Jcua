# Sandboxed benchmark: jcua vs cua (offline layers)

Scope: offline decision/eval layers in Docker (`--network=none`, no keys, 4 CPU / 4GB).
NOT end-to-end GUI driving — that needs VMs + hours (cua-bench class) and is future work.

## Result (2026-09-21, image `jcua-bench`, 300MB)

| side | stage | result |
| --- | --- | --- |
| jcua | pytest (14 tests) | pass, 0.44s |
| jcua | golden retrieval gate | 3/3 pass |
| jcua | retrieval latency | 0.01 ms/rank |
| jcua | guard fallback (keyless) | harmless APPROVE / dangerous ESCALATE, 0.01 ms |
| cua | s1-forms demo (local decider) | 196/196 top-1 @ 10.9 ms/element CPU, 706k params |

Host (unthrottled) S1 number for reference: 6.7 ms/element.

## Reading

- cua-s1 wins form-filling outright (perfect transfer, tiny, offline) — jcua has no
  fill decider yet. Gap, not rivalry: the plan is to wire S1 in as Jcua's fill
  decider (docs/S1-FORMS.md).
- jcua wins breadth: retrieve-or-create library, promotion gate, destructive-action
  guard, cross-platform targets, audit trail. None of that exists in libs/cua-s1.
- Live Jev guard (APPROVE/DENY @1.0) was proven on host with key; excluded here
  because the sandbox carries no credentials by design.

## Reproduce

See `evals/bench/README.md`.
