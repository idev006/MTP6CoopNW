from __future__ import annotations

from dataclasses import dataclass, field

from mtp6coopnw.security.access import HostIdentityRegistry


@dataclass(slots=True)
class AgentInitiatedSessionGuard:
    identities: HostIdentityRegistry
    _last_sequence: dict[str, int] = field(default_factory=dict)

    def accept(
        self,
        *,
        host_id: str,
        certificate: bytes,
        sequence: int,
        initiated_by_agent: bool,
    ) -> str:
        if not initiated_by_agent:
            raise PermissionError("production control channel must be agent-initiated")
        self.identities.verify(host_id, certificate)
        if sequence < 1:
            raise ValueError("sequence must be >= 1")
        previous = self._last_sequence.get(host_id, 0)
        if sequence <= previous:
            return "REPLAY"
        self._last_sequence[host_id] = sequence
        return "ACCEPTED"
