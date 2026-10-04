from __future__ import annotations

import hashlib
from dataclasses import dataclass
from enum import StrEnum


class Role(StrEnum):
    VIEWER = "viewer"
    OPERATOR = "operator"
    ADMIN = "admin"


@dataclass(frozen=True, slots=True)
class ActorContext:
    actor_id: str
    role: Role


_PERMISSION = {
    Role.VIEWER: {"view"},
    Role.OPERATOR: {"view", "preview", "operate", "maintenance"},
    Role.ADMIN: {"view", "preview", "operate", "maintenance", "configure", "emergency"},
}


def authorize(actor: ActorContext, permission: str) -> None:
    if permission not in _PERMISSION[actor.role]:
        raise PermissionError(f"{actor.role} cannot {permission}")


def certificate_fingerprint(pem_or_der: bytes) -> str:
    return hashlib.sha256(pem_or_der).hexdigest()


@dataclass(slots=True)
class HostIdentityRegistry:
    fingerprints: dict[str, str]

    def verify(self, host_id: str, presented_certificate: bytes) -> None:
        expected = self.fingerprints.get(host_id)
        if expected is None:
            raise PermissionError("unknown host identity")
        if certificate_fingerprint(presented_certificate) != expected:
            raise PermissionError("certificate does not match host identity")
