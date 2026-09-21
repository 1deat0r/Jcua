# Fork provenance

- Upstream: https://github.com/trycua/cua.git (MIT) — `libs/python` (computer, agent, core, som, computer-server, mcp-server), `libs/typescript`, `lume`, `qemu-docker`, `kasm`, `xfce`, `cua-bench`.
- Local base inspected: `~/.cua/cbregistry` at `c0a655c9c` (2026-09-21). Driver: `cua-driver 0.28.2`.
- What Jcua keeps: computer/agent abstractions, sandbox providers, bench harness shape, driver snapshot-before-action contract.
- What Jcua changes: Jev as the single decider (`src/jcua/jev_gates.py`), Jeva-style library/evolve/audit loop, Android via ARTEMIS (upstream has no Android actuator), unified `jcua run --target linux|windows|macos|android` CLI.
- License: MIT with upstream attribution in LICENSE.
