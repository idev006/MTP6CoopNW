# 23 — Master Use Case & Capability Matrix

- Status: ACTIVE SSOT
- Date: 2026-10-04
- Scope: Network-control capabilities for Client hosts and Database Server hosts
- Principle: Document First → Implementation Second → Evidence Always
- Engineering/Sandbox completion: 72/72 use cases
- Production acceptance: pending controlled real-world integration where flagged

## 1. Purpose

This document is the master functional baseline for MTP6CoopNW. Every important capability must map to:
1. an actor and use case,
2. an Engine/Application owner,
3. a Facade/API contract,
4. observable events,
5. automated tests,
6. a production acceptance check.

A feature is not considered complete merely because a UI control exists.

## 2. Primary actors

| Actor | Responsibility |
|---|---|
| Operator | Monitor hosts, review alarms, preview changes, execute permitted controls |
| Administrator | Configure hosts, schedules, network policy, maintenance and exceptions |
| Read-only Viewer | Observe status, alarms, policy and history without mutations |
| Central Control Core | Authoritative desired state, orchestration, monitoring and alarms |
| Local Agent | Read actual host state, enforce approved policy, verify and report |
| Client Host | Managed workstation/client endpoint |
| Database Server Host | Managed SQL/database endpoint with stricter safety rules |
| Scheduler | Evaluate time-based policy |
| Policy Engine | Resolve effective policy and priority |
| Planner | Produce dry-run changes and safety interlocks |
| Operation Engine | Execute bounded apply/verify/rollback lifecycle |
| Reconciliation Engine | Detect and repair drift |
| UI/Event Consumer | Render snapshot and event deltas without owning business rules |

## 3. Capability matrix

Status vocabulary:
- IMPLEMENTED: engine/application behavior exists.
- TESTED-SANDBOX: automated/simulated evidence exists.
- INTEGRATION-PENDING: requires real Windows/SQL/network validation.
- FUTURE: intentionally deferred.

| ID | Capability / Use case | Primary actor | Engine / owner | UI Facade / contract | Main events | Current status |
|---|---|---|---|---|---|---|
| UC-HOST-001 | Register managed host | Administrator/Core | ControlCore / HostRegistry | ReadOnlyControlFacade | host.registered | TESTED-SANDBOX |
| UC-HOST-002 | View all managed hosts | Operator/Viewer | ControlCore | UiApplicationFacade bootstrap | host.* | TESTED-SANDBOX |
| UC-HOST-003 | Logical ON/OFF per client | Operator/Admin | Policy + Planner + Operation | Command facade (real enforcement pending) | operation.stage_changed, host.* | TESTED-SANDBOX |
| UC-HOST-004 | Maintenance mode per host | Operator/Admin | Policy Engine | ControlApplicationFacade | policy.evaluated | TESTED-SANDBOX |
| UC-HOST-005 | Emergency disable | Administrator | Policy Engine | Command facade | policy.evaluated, operation.* | TESTED-SANDBOX |
| UC-HOST-006 | Manual override with higher priority than schedule | Operator/Admin | Policy Engine | ControlApplicationFacade | policy.evaluated | TESTED-SANDBOX |
| UC-NET-001 | Internet ON/OFF per host | Operator/Admin | Policy + Firewall adapter | Command facade | operation.*, drift.* | TESTED-SANDBOX / INTEGRATION-PENDING |
| UC-NET-002 | LAN access independent from Internet access | Administrator | Policy + Network/Firewall adapters | Command facade | operation.*, drift.* | TESTED-SANDBOX / INTEGRATION-PENDING |
| UC-NET-003 | Database access independent from Internet | Administrator | Policy + Firewall/SQL adapters | Command facade | operation.*, drift.* | TESTED-SANDBOX / INTEGRATION-PENDING |
| UC-NET-004 | Allowed ports per host | Administrator | Policy/Planner | Command facade | policy.evaluated, operation.* | TESTED-SANDBOX / INTEGRATION-PENDING |
| UC-NET-005 | Protocol-aware rules (TCP/UDP) | Administrator | Policy/Firewall adapter | Command facade | operation.* | TESTED-SANDBOX / INTEGRATION-PENDING |
| UC-NET-006 | Direction-aware rules (inbound/outbound) | Administrator | Policy/Firewall adapter | Command facade | operation.* | TESTED-SANDBOX / INTEGRATION-PENDING |
| UC-NET-007 | Destination-restricted rules, e.g. TCP 1433 only to DB Server | Administrator | Policy/Firewall adapter | Command facade | operation.* | TESTED-SANDBOX / INTEGRATION-PENDING |
| UC-NET-008 | Prevent WAN exposure of SQL | Safety/Admin | Safety policy + Firewall adapter | Safety interlock | alarm.*, operation.* | TESTED-SANDBOX / INTEGRATION-PENDING |
| UC-SCH-001 | Schedule host usage by weekday and time | Administrator | Scheduler/Policy Engine | Policy facade | policy.evaluated | TESTED-SANDBOX |
| UC-SCH-002 | Schedule Internet access by weekday and time | Administrator | Scheduler/Policy Engine | Policy facade | policy.evaluated | TESTED-SANDBOX |
| UC-SCH-003 | Different schedule per host | Administrator | Scheduler/Policy Engine | Policy facade | policy.evaluated | TESTED-SANDBOX |
| UC-SCH-004 | Different schedule per day | Administrator | Scheduler/Policy Engine | Policy facade | policy.evaluated | TESTED-SANDBOX |
| UC-SCH-005 | Overnight schedule crossing midnight | Administrator | Scheduler | Policy facade | policy.evaluated | TESTED-SANDBOX |
| UC-SCH-006 | Timezone-aware evaluation | Administrator | Scheduler | Policy facade | policy.evaluated | TESTED-SANDBOX |
| UC-SCH-007 | Holiday / special-date exceptions | Administrator | Scheduler | Policy facade | policy.evaluated | TESTED-SANDBOX |
| UC-SCH-008 | Temporary access with automatic expiry | Operator/Admin | Policy + Scheduler | Command facade | policy.evaluated, operation.* | TESTED-SANDBOX |
| UC-POL-001 | Priority resolution: Safety > Emergency > Manual > Maintenance > Schedule > Default | Policy Engine | Policy Engine | ControlApplicationFacade | policy.evaluated | TESTED-SANDBOX |
| UC-POL-002 | Policy revisioning | Core/Agent | VersionedPolicyStore | Policy facade | policy.staged | TESTED-SANDBOX |
| UC-POL-003 | Duplicate policy idempotency | Core/Agent | VersionedPolicyStore | Policy facade | policy.staged | TESTED-SANDBOX |
| UC-POL-004 | Reject stale policy replay | Core/Agent | VersionedPolicyStore | Policy facade | policy.* | TESTED-SANDBOX |
| UC-POL-005 | Detect same-revision conflict | Core/Agent | VersionedPolicyStore | Policy facade | policy.* | TESTED-SANDBOX |
| UC-POL-006 | Last-known-valid policy survives Core loss | Agent | PolicyStore | Agent runtime | agent/core events | TESTED-SANDBOX / INTEGRATION-PENDING |
| UC-PLAN-001 | Dry-run / preview effective policy | Operator/Admin | Policy Engine | ControlApplicationFacade.preview | policy.evaluated | TESTED-SANDBOX |
| UC-PLAN-002 | Plan exact changes before apply | Operator/Admin | Planner | ControlApplicationFacade.plan | operation.plan_created | TESTED-SANDBOX |
| UC-PLAN-003 | Block unsafe change if control/LAN path unhealthy | Planner | Planner interlock | Command facade | operation.* | TESTED-SANDBOX |
| UC-OPS-001 | Apply bounded operation | Operation Engine | Operation Engine | Command facade | operation.stage_changed | TESTED-SANDBOX |
| UC-OPS-002 | Read-back verification | Operation Engine | Operation Engine | Command facade | operation.stage_changed | TESTED-SANDBOX |
| UC-OPS-003 | Roll back failed apply | Operation Engine | Operation Engine | Command facade | operation.stage_changed | TESTED-SANDBOX |
| UC-OPS-004 | Roll back failed verification | Operation Engine | Operation Engine | Command facade | operation.stage_changed | TESTED-SANDBOX |
| UC-OPS-005 | Operation timeout | Operation Engine | Operation Engine | Command facade | operation.stage_changed | TESTED-SANDBOX |
| UC-OPS-006 | Idempotent operation IDs across retries | Core/Agent | Operation contract | Command facade | operation.* | TESTED-SANDBOX / INTEGRATION-PENDING |
| UC-REC-001 | Detect desired-vs-actual drift | Reconciliation | detect_drift | ControlApplicationFacade | drift.detected | TESTED-SANDBOX |
| UC-REC-002 | Reconcile drift to desired state | Reconciliation | ReconciliationEngine | ControlApplicationFacade | drift.reconciled | TESTED-SANDBOX |
| UC-MON-001 | Heartbeat monitoring | Core/Agent | ReadOnlyAgent + ControlCore | ReadOnlyControlFacade | host.telemetry_updated | TESTED-SANDBOX |
| UC-MON-002 | ONLINE / STALE / OFFLINE freshness | Core | HostRegistry | UiApplicationFacade | host.freshness_changed | TESTED-SANDBOX |
| UC-MON-003 | HEALTHY / DEGRADED / UNKNOWN | Core | Agent status + Core | UiApplicationFacade | host.telemetry_updated | TESTED-SANDBOX |
| UC-MON-004 | SQL service/reachability monitoring | Agent | SQL adapter | ReadOnlyControlFacade | agent heartbeat | TESTED-SANDBOX / INTEGRATION-PENDING |
| UC-MON-005 | Firewall state monitoring | Agent | Firewall adapter | ReadOnlyControlFacade | agent heartbeat | TESTED-SANDBOX / INTEGRATION-PENDING |
| UC-MON-006 | Network/interface/route monitoring | Agent | Network adapter | ReadOnlyControlFacade | agent heartbeat | TESTED-SANDBOX / INTEGRATION-PENDING |
| UC-MON-007 | Windows service monitoring | Agent | Service adapter | ReadOnlyControlFacade | agent heartbeat | TESTED-SANDBOX / INTEGRATION-PENDING |
| UC-ALM-001 | Raise stale/offline/degraded alarms | Core | Alarm evaluation | ReadOnlyControlFacade | alarm lifecycle / host events | TESTED-SANDBOX |
| UC-ALM-002 | Alarm clear lifecycle | Core | Alarm lifecycle | UI facade | alarm.cleared | TESTED-SANDBOX |
| UC-ALM-003 | Alarm acknowledgement | Operator | Alarm service | UI facade | alarm.acknowledged | TESTED-SANDBOX |
| UC-UI-001 | One-time dashboard snapshot | UI | UI Application Facade | bootstrap_dashboard | n/a | TESTED-SANDBOX |
| UC-UI-002 | Reactive UI updates without status polling | UI | Event Bus + SSE | next_ui_events / SseEventGateway | all UI events | TESTED-SANDBOX |
| UC-UI-003 | Resume from event sequence after reconnect | UI | Event Bus | UiEventGateway | sequence | TESTED-SANDBOX |
| UC-UI-004 | Force snapshot resync after replay gap | UI | Event Bus | UiEventGateway | system.resync_required | TESTED-SANDBOX |
| UC-UI-005 | Display operation progress in real time | UI | Operation Engine | Presenter/ViewModel | operation.stage_changed | TESTED-SANDBOX |
| UC-UI-006 | Test presenter/view-model with Fake Facade only | QA | DashboardBackend Protocol | FakeDashboardFacade | synthetic events | TESTED-SANDBOX |
| UC-AUD-001 | Structured audit for host/policy/operation activity | Admin/Auditor | AuditStore | future audit query facade | audit events | TESTED-SANDBOX |
| UC-AUD-002 | Identify actor who initiated mutation | Admin/Auditor | Auth + Audit | command facade | audit | TESTED-SANDBOX / INTEGRATION-PENDING |
| UC-SEC-001 | No arbitrary remote shell | Security | Transport/Agent boundary | n/a | audit | TESTED-SANDBOX |
| UC-SEC-002 | Agent-initiated authenticated transport | Security | Transport adapter | n/a | connectivity events | TESTED-SANDBOX / INTEGRATION-PENDING |
| UC-SEC-003 | mTLS host identity binding | Security | Transport adapter | n/a | connectivity events | TESTED-SANDBOX / INTEGRATION-PENDING |
| UC-SEC-004 | Least-privilege SQL/application credentials | Security/Admin | Deployment | n/a | audit | TESTED-SANDBOX / INTEGRATION-PENDING |
| UC-RES-001 | Core restart recovery | Core | persistence/replay | UI reconnect | replay/resync | TESTED-SANDBOX / INTEGRATION-PENDING |
| UC-RES-002 | Agent restart recovery | Agent | local policy persistence | heartbeat/policy replay | telemetry | TESTED-SANDBOX / INTEGRATION-PENDING |
| UC-RES-003 | Core unavailable while Agent continues last-known policy | Agent | Agent runtime | UI alarm after timeout | host.freshness_changed | TESTED-SANDBOX / INTEGRATION-PENDING |
| UC-RES-004 | Whole-site outage convergence | Core | freshness engine | UI events | host.freshness_changed | TESTED-SANDBOX |
| UC-RES-005 | Clock skew / replay anomaly handling | Core | telemetry validation | read-only facade | telemetry rejected | TESTED-SANDBOX |
| UC-DB-001 | DB normal mode: LAN/SQL available, Internet denied by default | Admin | Policy Engine | Policy/Command facade | policy/operation events | TESTED-SANDBOX / INTEGRATION-PENDING |
| UC-DB-002 | DB maintenance: temporary Internet allowed while LAN/SQL preserved | Admin | Policy Engine | Policy/Command facade | policy/operation events | TESTED-SANDBOX / INTEGRATION-PENDING |
| UC-DB-003 | Never expose SQL service to WAN | Safety | Safety policy | Safety interlock | alarm/operation | TESTED-SANDBOX / INTEGRATION-PENDING |
| UC-SCL-001 | Add new client without changing engine architecture | Admin | Registry/Composition | UI facade | host.registered | TESTED-SANDBOX |
| UC-SCL-002 | Replace UI technology without changing engines | Engineering | Facades/Protocols | DashboardBackend | n/a | TESTED-SANDBOX |
| UC-SCL-003 | Replace fake adapters with Windows/SQL adapters | Engineering | Ports/Adapters | n/a | n/a | TESTED-SANDBOX |

## 4. Mandatory acceptance scenarios before real-site rollout

1. Client Internet ON/OFF while LAN and Core reachability remain intact.
2. Client SQL access allowed while Internet is denied.
3. Per-client allowed-port policy with protocol/direction/destination restrictions.
4. Schedule transition at exact start/end time and across midnight.
5. Manual override and automatic return to normal policy.
6. DB normal mode and maintenance mode.
7. SQL remains unreachable from WAN during every DB mode.
8. Apply failure and verification failure both roll back safely.
9. Loss of Core does not cause Agent to become permissive.
10. Core/Agent restart restores last-known-valid state.
11. Event stream reconnect/replay/resync behaves deterministically.
12. Audit evidence identifies what changed, when, target host, result and initiating actor.
13. No command can disable the only management path without an approved recovery mechanism.
14. Whole-site outage produces bounded OFFLINE state and alarm convergence.
15. Restore/recovery test returns all managed hosts to intended policy.

## 5. Definition of Done for a use case

A use case reaches DONE only when all applicable items are satisfied:
- documented contract and safety semantics,
- implementation behind stable facade/port,
- unit or contract test,
- scenario/failure-path test,
- observable result/event,
- audit evidence for mutations,
- real integration acceptance where OS/network/SQL behavior is involved.

## 6. Current overall interpretation

The engine/application and sandbox model covers the majority of the control-system behavior. Items marked INTEGRATION-PENDING are not missing concepts; they require controlled proof against real Windows Firewall, routes, SQL Server, service lifecycle, persistence and authenticated transport before production acceptance.
