from __future__ import annotations

import copy
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from mtp6coopnw.application import (
    CommandExecutionResult,
    ControlState,
    OperationService,
    PlanningService,
    PolicyEvaluationService,
    StateReporter,
)
from mtp6coopnw.operations import MutableHost


@dataclass(slots=True)
class EngineCommandExecutor:
    """Application service bridging control intent to domain engines."""

    policy_engine: PolicyEvaluationService
    planner: PlanningService
    operation_engine: OperationService
    hosts: dict[str, MutableHost]
    policy_by_host: dict[str, dict[str, Any]] = field(default_factory=dict)
    state_reporter: StateReporter | None = None

    def apply(
        self,
        *,
        host_id: str,
        desired: dict[str, Any],
        now: datetime,
    ) -> CommandExecutionResult:
        host = self.hosts[host_id]
        policy = self._base_policy(host_id, host)
        revision = int(policy.get("policy_revision", 0)) + 1
        policy["policy_revision"] = revision

        if "hostEnabled" in desired:
            policy.setdefault("host", {})["enabled"] = bool(desired["hostEnabled"])
        if "internetAllowed" in desired:
            policy.setdefault("internet", {})["allowed"] = bool(
                desired["internetAllowed"]
            )
        if "databaseAllowed" in desired:
            policy.setdefault("database", {})["allowed"] = bool(
                desired["databaseAllowed"]
            )
        if "portRules" in desired:
            rules = desired["portRules"]
            if not isinstance(rules, list):
                raise ValueError("portRules must be a list")
            managed: set[int] = set()
            for rule in rules:
                if not isinstance(rule, dict):
                    raise ValueError("each port rule must be an object")
                port = rule.get("port")
                allowed = rule.get("allowed", True)
                if (
                    not isinstance(port, int)
                    or isinstance(port, bool)
                    or not 1 <= port <= 65535
                ):
                    raise ValueError("port must be integer in 1..65535")
                if bool(allowed):
                    managed.add(port)
            policy.setdefault("ports", {})["managed"] = sorted(managed)

        effective = self.policy_engine.evaluate(
            host_id=host_id,
            now=now,
            policy=policy,
        )
        plan = self.planner.plan(desired=effective, actual=host.state)
        result = self.operation_engine.execute(plan=plan, host=host, now=now)

        # Desired state remains authoritative even if enforcement rolled back.
        self.policy_by_host[host_id] = copy.deepcopy(policy)
        state = self._state(host)

        if self.state_reporter is not None:
            self.state_reporter.report(
                host_id=host_id,
                state=state.to_dict(),
                policy_revision=revision,
                now=now,
            )

        return CommandExecutionResult(
            operation_id=result.operation_id,
            stage=result.stage.value,
            rolled_back=result.rolled_back,
            error=result.error,
            policy_revision=revision,
            state=state,
        )

    def _base_policy(self, host_id: str, host: MutableHost) -> dict[str, Any]:
        existing = self.policy_by_host.get(host_id)
        if existing is not None:
            return copy.deepcopy(existing)
        return {
            "policy_revision": 0,
            "host": {"enabled": host.state.host_enabled},
            "internet": {"allowed": host.state.internet_allowed},
            "database": {"allowed": host.state.database_allowed},
            "ports": {"managed": list(host.state.allowed_ports)},
        }

    @staticmethod
    def _state(host: MutableHost) -> ControlState:
        state = host.state
        return ControlState(
            host_enabled=state.host_enabled,
            internet_allowed=state.internet_allowed,
            database_allowed=state.database_allowed,
            allowed_ports=state.allowed_ports,
            lan_reachable=state.lan_reachable,
            control_reachable=state.control_reachable,
        )
