from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


class ReadPolicyStore(Protocol):
    def get(self, host_id: str) -> dict[str, Any] | None: ...


@dataclass(frozen=True, slots=True)
class RecoveryDecision:
    mode: str
    policy: dict[str, Any] | None


def recover_agent_policy(host_id: str, store: ReadPolicyStore) -> RecoveryDecision:
    policy = store.get(host_id)
    if policy is None:
        return RecoveryDecision("SAFE_HOLD", None)
    revision = policy.get("policy_revision")
    if not isinstance(revision, int) or isinstance(revision, bool) or revision < 1:
        return RecoveryDecision("SAFE_HOLD", None)
    return RecoveryDecision("LAST_KNOWN_VALID", policy)
