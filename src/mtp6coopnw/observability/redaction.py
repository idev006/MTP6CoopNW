from __future__ import annotations

from typing import Any

_REDACTED = "***REDACTED***"
_DEFAULT_SECRET_KEYS = {
    "password",
    "passwd",
    "secret",
    "token",
    "access_token",
    "refresh_token",
    "api_key",
    "private_key",
    "credential",
    "credentials",
}


def redact_mapping(
    value: dict[str, Any],
    *,
    secret_keys: set[str] | None = None,
) -> dict[str, Any]:
    keys = {key.lower() for key in (secret_keys or _DEFAULT_SECRET_KEYS)}
    return _redact_dict(value, keys)


def _redact_dict(value: dict[str, Any], secret_keys: set[str]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, item in value.items():
        if key.lower() in secret_keys:
            result[key] = _REDACTED
        elif isinstance(item, dict):
            result[key] = _redact_dict(item, secret_keys)
        elif isinstance(item, list):
            result[key] = [_redact_item(child, secret_keys) for child in item]
        else:
            result[key] = item
    return result


def _redact_item(value: Any, secret_keys: set[str]) -> Any:
    if isinstance(value, dict):
        return _redact_dict(value, secret_keys)
    if isinstance(value, list):
        return [_redact_item(child, secret_keys) for child in value]
    return value
