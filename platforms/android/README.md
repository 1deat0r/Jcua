# android target — via ARTEMIS MCP + adb (not cua-driver)

Requires device/emulator + `adb` on PATH, ARTEMIS repo with `.env` key (`GEMINI_API_KEY` default).
Flow: `mobile_diagnose` -> `mobile_run_task` (detached) -> monitor -> verify from fresh device state.
