# Jcua — Jev Computer Use Agent

Cross-platform self-improving computer-use agent. Fork-offshoot of [trycua/cua](https://github.com/trycua/cua) (MIT), re-brained around TypeSafe Jev decisions + a Jeva-style self-improvement loop.

`Jcua` (this repo, capital J) is the project. `jcua` (lowercase) is the CLI/package.

## Platforms

- Linux + distros (X11 AT-SPI + XSendEvent, Wayland helper, Docker/QEMU sandboxes, Xfce)
- Windows (UIA tree, UWP/ApplicationFrameHost aware)
- macOS (AX tree, Lume virtualization)
- Android (ARTEMIS via MCP + adb — cua-driver does not cover Android)

## Layout

- `src/jcua/` — agent core: computer abstraction, Jev gates, evolve loop
- `platforms/<os>/` — per-OS drivers, deps, quirks
- `library/` — versioned skills/tools/workflows (Jeva-style reuse-or-create)
- `memory/` — trust-tagged facts + cluster notes
- `traces/` — `trace.jsonl` per run
- `evals/golden/` — golden tasks + gate
- `docs/ARCHITECTURE.md` — system design
- `docs/FORK.md` — what was forked from cua, what changed
- `scripts/sync-upstream.sh` — pull upstream trycua/cua without clobbering jcua layers

## Quickstart

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
export TYPESAFE_API_KEY="..."   # read at call time, never logged
jcua run "Open the browser to example.com and report the title" --budget 0.50
jcua library list
jcua eval --golden
```

Android (requires device/emulator + adb, ARTEMIS wired as MCP):

```bash
jcua run "On Android, open Settings and report the OS version" --target android
```

## Upstream

Upstream remote: `https://github.com/trycua/cua.git` (MIT). See `docs/FORK.md`.
`cua-driver` binary (0.28.2+) is reused as the desktop actuator until `jcua-driver` (Rust) lands.

## License

MIT — see `LICENSE` (upstream attribution retained).
