from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SqlCredentialPolicy:
    username: str
    permissions: tuple[str, ...]

    def validate(self) -> None:
        if not self.username or self.username.casefold() == "sa":
            raise ValueError("SQL application credential must not use sa")
        forbidden = {"sysadmin", "securityadmin", "serveradmin"}
        normalized = {permission.casefold() for permission in self.permissions}
        if forbidden & normalized:
            raise ValueError("SQL application credential is over-privileged")
        if not self.permissions:
            raise ValueError("least-privilege permission set is required")
