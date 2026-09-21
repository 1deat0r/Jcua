# Jcua architecture (v0.1.0)

`Computer` (per-OS) -> `Jev gates` (choice/noul routing) -> `executor` (typed actions) -> `verify` (re-capture) -> `trace + library + evals`.

- Desktop: cua-driver underneath. Capture first (`som`), click by element index, `capture_after=True`, climb verify->escalate ladder (background -> px -> foreground) only on driver verdict.
- Android: ARTEMIS MCP `mobile_run_task` (detached device agent) + adb. Hermes dispatches/monitors/verifies.
- Brain split: Jev picks operation+target in one request; small OpenAI-compatible LLM writes field text only on TYPE_TEXT. No screenshots in Jev loop; pixels only for verify.
- Self-improvement (from jeva): retrieve top-k -> reuse-or-create -> execute -> judge -> meter/reward -> trace + stats + memory. Mutations dry-run by default, promotion gated.
