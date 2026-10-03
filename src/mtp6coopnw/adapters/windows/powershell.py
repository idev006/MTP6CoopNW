from __future__ import annotations

import base64
import json
import pathlib
import subprocess
from dataclasses import dataclass, field
from typing import Any


class PowerShellBridgeError(RuntimeError):
    """Raised when an allowlisted PowerShell adapter operation fails."""


_DEFAULT_OPERATIONS: dict[str, tuple[str, str]] = {
    "network.state": ("MTP6.Network/MTP6.Network.psm1", "Get-MTP6NetworkState"),
    "network.routes": ("MTP6.Network/MTP6.Network.psm1", "Get-MTP6RouteState"),
    "network.lan_test": ("MTP6.Network/MTP6.Network.psm1", "Test-MTP6LanReachability"),
    "network.internet_test": (
        "MTP6.Network/MTP6.Network.psm1",
        "Test-MTP6InternetReachability",
    ),
    "firewall.managed_state": (
        "MTP6.Firewall/MTP6.Firewall.psm1",
        "Get-MTP6ManagedFirewallState",
    ),
    "firewall.drift": ("MTP6.Firewall/MTP6.Firewall.psm1", "Test-MTP6FirewallDrift"),
    "services.state": ("MTP6.Services/MTP6.Services.psm1", "Get-MTP6ServiceState"),
    "sql.service_state": ("MTP6.Sql/MTP6.Sql.psm1", "Get-MTP6SqlServiceState"),
    "sql.tcp_test": ("MTP6.Sql/MTP6.Sql.psm1", "Test-MTP6SqlTcp"),
}


@dataclass(slots=True)
class PowerShellReadOnlyBridge:
    module_root: pathlib.Path
    executable: str = "pwsh"
    timeout_seconds: int = 20
    operations: dict[str, tuple[str, str]] = field(
        default_factory=lambda: dict(_DEFAULT_OPERATIONS)
    )

    def invoke(
        self,
        operation: str,
        parameters: dict[str, Any] | None = None,
    ) -> Any:
        try:
            relative_module, function_name = self.operations[operation]
        except KeyError as exc:
            raise PowerShellBridgeError(f"Operation is not allowlisted: {operation}") from exc

        module_path = (self.module_root / relative_module).resolve()
        if not module_path.is_file():
            raise PowerShellBridgeError(f"PowerShell module not found: {module_path}")

        payload = json.dumps(parameters or {}, separators=(",", ":")).encode("utf-8")
        encoded = base64.b64encode(payload).decode("ascii")
        escaped_path = str(module_path).replace("'", "''")

        script = (
            f"Import-Module '{escaped_path}' -Force -ErrorAction Stop; "
            f"$raw=[Text.Encoding]::UTF8.GetString([Convert]::FromBase64String('{encoded}')); "
            "$obj=$raw | ConvertFrom-Json; "
            "$params=@{}; "
            "if ($null -ne $obj) { "
            "$obj.PSObject.Properties | ForEach-Object { $params[$_.Name]=$_.Value } "
            "}; "
            f"$result=& '{function_name}' @params; "
            "$result | ConvertTo-Json -Depth 8 -Compress"
        )

        try:
            completed = subprocess.run(
                [
                    self.executable,
                    "-NoProfile",
                    "-NonInteractive",
                    "-Command",
                    script,
                ],
                check=False,
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise PowerShellBridgeError(
                f"PowerShell invocation failed for operation: {operation}"
            ) from exc

        if completed.returncode != 0:
            error = completed.stderr.strip() or "unknown PowerShell error"
            raise PowerShellBridgeError(f"{operation} failed: {error}")

        output = completed.stdout.strip()
        if not output:
            return None

        try:
            result: Any = json.loads(output)
        except json.JSONDecodeError as exc:
            raise PowerShellBridgeError(
                f"{operation} returned invalid JSON"
            ) from exc
        return result
