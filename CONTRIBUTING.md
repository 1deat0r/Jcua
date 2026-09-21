# Contributing to Jcua

- Branch from `main`: `feat/<scope>`, `fix/<scope>`, `docs/<scope>`. One concern per PR.
- Conventional commits: `feat:`, `fix:`, `docs:`, `chore:`, `eval:`.
- Jev stays a decider (`src/jcua/jev_gates.py` only), default OFF, fail-safe declared, key via env only.
- Background-first desktop; verify by re-capture; no destructive probing on live data.
- Every behavior PR needs: command(s) run, fresh-state evidence, golden status.
