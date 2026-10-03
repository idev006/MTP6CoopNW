from __future__ import annotations

import copy
import json
import os
import pathlib
import tempfile
from dataclasses import dataclass
from typing import Any


class PolicyCacheError(RuntimeError):
    """Raised when the local last-known policy cache cannot be read or written."""


@dataclass(slots=True)
class JsonFilePolicyStore:
    """Small atomic runtime cache for last-known validated policies.

    This is runtime state, not human-authored configuration. Human/site configuration
    remains TOML-first.
    """

    path: pathlib.Path

    def get(self, host_id: str) -> dict[str, Any] | None:
        all_policies = self._read_all()
        value = all_policies.get(host_id)
        return copy.deepcopy(value) if isinstance(value, dict) else None

    def save(self, host_id: str, policy: dict[str, Any]) -> None:
        all_policies = self._read_all()
        all_policies[host_id] = copy.deepcopy(policy)
        self._atomic_write(all_policies)

    def _read_all(self) -> dict[str, Any]:
        if not self.path.exists():
            return {}

        try:
            raw = self.path.read_text(encoding="utf-8")
            parsed = json.loads(raw)
        except (OSError, json.JSONDecodeError) as exc:
            raise PolicyCacheError(f"Cannot read policy cache: {self.path}") from exc

        if not isinstance(parsed, dict):
            raise PolicyCacheError("Policy cache root must be a JSON object")
        return parsed

    def _atomic_write(self, data: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2)

        temp_name: str | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=self.path.parent,
                prefix=f".{self.path.name}.",
                suffix=".tmp",
                delete=False,
            ) as handle:
                temp_name = handle.name
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())

            pathlib.Path(temp_name).replace(self.path)
        except OSError as exc:
            if temp_name is not None:
                pathlib.Path(temp_name).unlink(missing_ok=True)
            raise PolicyCacheError(f"Cannot write policy cache: {self.path}") from exc
