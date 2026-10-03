from __future__ import annotations

import hashlib
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class ConfigError(ValueError):
    """Raised when configuration cannot be loaded or validated."""


@dataclass(frozen=True, slots=True)
class LoadedToml:
    path: Path
    data: dict[str, Any]
    sha256: str


def load_toml(path: Path) -> LoadedToml:
    """Load TOML and return parsed data plus a deterministic content hash."""
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise ConfigError(f"Cannot read TOML file: {path}") from exc

    try:
        data = tomllib.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, tomllib.TOMLDecodeError) as exc:
        raise ConfigError(f"Invalid TOML file: {path}") from exc

    if not isinstance(data, dict):
        raise ConfigError(f"TOML root must be a table: {path}")

    digest = hashlib.sha256(raw).hexdigest()
    return LoadedToml(path=path, data=data, sha256=digest)
