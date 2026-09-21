# Jcua agent guide

Read README.md, docs/ARCHITECTURE.md and docs/FORK.md before implementation.

- Canonical path only: `/run/media/its1deat0r/Projects/Tools/Jcua`. Do not create shadow copies under `~/code/`, `~/apps/`, or home. Use the `/run/media/` form in all new references (`/mnt/data` is the same disk).
- Fork hygiene: keep upstream at git remote `upstream` (`https://github.com/trycua/cua.git`). Sync via `scripts/sync-upstream.sh`. Never force-push upstream history into `main` blindly; review `libs/python`, `libs/typescript` diffs first.
- Jev is a decider, not a generator: `choice`/`noul`/`score` via `POST https://api.typesafe.ai/v1/systemone`, model `jev-latest`, key from `TYPESAFE_API_KEY` read at call time — never logged, stored, or printed. Gate behind config, default OFF, with fail-safe per feature (approvals fail to escalate, recall gates fail open, routing fails to legacy).
- One shared transport only: all Jev calls go through `src/jcua/jev_gates.py`. No second client.
- Background-first desktop: snapshot before action, click by element index, verify by re-capture. Never steal foreground input to discover behavior. Never click destructive controls, submit, publish, or alter live data to discover behavior — use isolated fixtures/VMs.
- Android via ARTEMIS MCP (`mobile_run_task`) + adb, not cua-driver. Diagnose with `mobile_diagnose` first. No iOS.
- Self-improvement: every run appends `traces/trace.jsonl` + stats; promotion needs `uses>=3 sr>=0.8 value>=median` + `golden_gate()` all-green; `library audit` must pass on file/DB mismatch. Dry-run default for mutations, `--apply` explicit.
- Never commit credentials, raw private captures, cookies, or user transcripts. `TYPESAFE_API_KEY`, `GEMINI/OPENAI/ANTHROPIC` keys stay in env.
- Validate: `python3 -m py_compile src/jcua/*.py` after core changes; `jcua eval --golden` before promotion claims.
