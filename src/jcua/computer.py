"""Computer abstraction — background-first, per-OS dispatch."""
from dataclasses import dataclass

@dataclass
class Computer:
    os_type: str = "linux"   # linux | windows | macos | android
    provider_type: str = "local"  # local | cloud | device

    def describe(self):
        if self.os_type == "android":
            return "android via ARTEMIS MCP + adb (not cua-driver)"
        return f"{self.os_type} via cua-driver (background-first, snapshot-before-action)"
