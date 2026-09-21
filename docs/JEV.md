# Jev gate #1 — destructive-action guard

Single shared transport: `src/jcua/jev_gates.py` (`decide` + `guard_action`). No second client.

## Schema (verified live 2026-09-21, model `jev-1.13.0`)

Envelope `{"state", "model", "questions"}`; question type `choice` with string
`options` plus a `criteria` mapping. The choice ranges over the **criteria keys**:

- `safe_to_proceed` → `APPROVE`
- `needs_human_review` → `ESCALATE`

(`yes_no` / `noul` bare types return 400; object-form `options: [{id}]` is ignored
by the model — string options + criteria mapping is the working shape.)

## Fail-safe

- Gate ships disabled (`jev.enabled: false`); disabled mode approves without network (legacy behavior).
- Keyless, transport failure, or invalid answer → heuristic fallback: destructive
  pattern → `ESCALATE`, else `APPROVE`.
- Live answer below `confidence_floor` (0.75) or `needs_human_review` → `ESCALATE`.
- Approvals fail to escalate; recall/routing fail to legacy. Key read from
  `TYPESAFE_API_KEY` at call time, never logged.

## Live probe (2026-09-21)

- `jcua guard "list files in the current directory"` → `APPROVE` 1.0 live
- `jcua guard "rm -rf /"` → `ESCALATE` 1.0 live

## Enabling

Owner flips `jev.enabled: true` in `jcua.config.yaml`; long-lived sessions pick it
up on restart. `jcua run` blocks on `ESCALATE` unless `--force`.
