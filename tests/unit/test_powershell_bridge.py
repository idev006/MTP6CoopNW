from __future__ import annotations

import json
import pathlib
import subprocess
from unittest.mock import patch

import pytest

from mtp6coopnw.adapters.windows import PowerShellBridgeError, PowerShellReadOnlyBridge


def _make_module(root: pathlib.Path) -> pathlib.Path:
    module = root / "MTP6.Network" / "MTP6.Network.psm1"
    module.parent.mkdir(parents=True)
    module.write_text("# test module", encoding="utf-8")
    return module


def test_bridge_rejects_unknown_operation(tmp_path: pathlib.Path) -> None:
    bridge = PowerShellReadOnlyBridge(module_root=tmp_path)

    with pytest.raises(PowerShellBridgeError, match="not allowlisted"):
        bridge.invoke("shell.arbitrary", {"Command": "whoami"})


def test_bridge_parses_structured_json(tmp_path: pathlib.Path) -> None:
    _make_module(tmp_path)
    bridge = PowerShellReadOnlyBridge(
        module_root=tmp_path,
        operations={
            "network.state": (
                "MTP6.Network/MTP6.Network.psm1",
                "Get-MTP6NetworkState",
            )
        },
    )
    expected = {"InterfaceAlias": "Ethernet", "InterfaceIndex": 4}
    completed = subprocess.CompletedProcess(
        args=["pwsh"],
        returncode=0,
        stdout=json.dumps(expected),
        stderr="",
    )

    with patch("subprocess.run", return_value=completed) as run:
        result = bridge.invoke("network.state")

    assert result == expected
    command = run.call_args.args[0]
    assert command[0] == "pwsh"
    assert "Get-MTP6NetworkState" in command[-1]


def test_bridge_surfaces_powershell_failure(tmp_path: pathlib.Path) -> None:
    _make_module(tmp_path)
    bridge = PowerShellReadOnlyBridge(
        module_root=tmp_path,
        operations={
            "network.state": (
                "MTP6.Network/MTP6.Network.psm1",
                "Get-MTP6NetworkState",
            )
        },
    )
    completed = subprocess.CompletedProcess(
        args=["pwsh"],
        returncode=1,
        stdout="",
        stderr="adapter failed",
    )

    with (
        patch("subprocess.run", return_value=completed),
        pytest.raises(PowerShellBridgeError, match="adapter failed"),
    ):
        bridge.invoke("network.state")
