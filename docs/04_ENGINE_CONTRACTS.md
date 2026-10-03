# 04 — Engine Contracts

## Contract Philosophy
Engine/Core เป็น authoritative control logic ของระบบ UI ทุกชนิดต้องเรียกผ่าน Application/Control contract เดียวกัน และ local Agent ต้อง enforce เฉพาะ command/policy ที่ผ่าน validation/authentication

## Common Result Contract
ทุก command ควรคืนข้อมูลอย่างน้อย:
- success
- operation
- target
- policyRevision
- stateBefore
- stateAfter
- checks[]
- warnings[]
- errors[]
- timestamp
- correlationId

## Common Host Status Contract
อย่างน้อย:
- hostId
- online
- lastHeartbeat
- effectiveState
- policyRevision
- scheduleState
- internetAllowed / internetActual
- databaseAllowed / databaseActual
- managedPorts[]
- alarms[]
- lastCommand

## PolicyEngine
Responsibilities:
- Validate policy
- Resolve priority
- Resolve manual override vs schedule
- Produce effective desired state
- Version policies

Suggested operations:
- GetEffectivePolicy(hostId)
- SetHostEnabled(hostId, enabled)
- SetUsageSchedule(hostId, schedule)
- SetInternetPolicy(hostId, policy)
- SetDatabasePolicy(hostId, policy)
- SetPortPolicy(hostId, rules)

## SchedulerEngine
Responsibilities:
- Evaluate per-host schedules
- Trigger desired-state reevaluation at boundaries
- Handle timezone and restart recovery

Suggested operations:
- ValidateSchedule()
- GetScheduleState(hostId)
- GetNextTransition(hostId)
- EvaluateNow(hostId)

## NetworkEngine
Responsibilities:
- Read adapter/IP/subnet/gateway/DNS state
- Validate target adapter
- Build network change plan
- Apply approved changes
- Verify LAN state
- Restore prior state when rollback is required

## FirewallEngine
Responsibilities:
- Inspect project-owned managed firewall rules
- Apply Internet/DB/port policy
- Restrict SQL inbound sources
- Detect drift
- Converge actual rules toward desired policy

Suggested operations:
- GetFirewallState()
- EnsureInternetPolicy()
- EnsureDatabasePolicy()
- EnsurePortPolicy()
- DetectDrift()

## SqlEngine
Responsibilities:
- Discover SQL-related Windows services
- Check service state
- Test configured/listening TCP port
- Test DB connectivity without modifying business data

## AccessControlEngine
Responsibilities:
- Resolve whether host is currently allowed
- Apply host-level enabled/disabled state through approved mechanisms
- Never bypass safety/control channel requirements

## AgentEngine
Responsibilities:
- Receive authenticated policy/command
- Persist last-known valid policy
- Enforce effective desired state
- Collect telemetry
- Send heartbeat
- Reconcile desired vs actual state
- Return structured command results

Suggested operations:
- Register()
- ApplyPolicy(revision)
- GetLocalState()
- Reconcile()
- Heartbeat()
- SelfTest()

## TelemetryEngine
Responsibilities:
- Aggregate state changes
- Publish heartbeat/status
- Normalize module telemetry
- Detect stale/offline agents

## MaintenanceEngine
Orchestrate Normal/Maintenance transitions using Policy, Network, Firewall, Diagnostics and Audit engines

## DiagnosticsEngine
Run non-destructive checks:
- LAN
- Router
- SQL port
- DNS
- Internet
- firewall policy
- schedule state
- agent health
- disk/service health

## BackupEngine
v1:
- Detect latest known backup
- Report age/status
- Validate configured backup path

## AuditEngine
- append-oriented operation records
- include policy revision, before/after/checks/result
- avoid secrets/passwords/tokens

## Communication Contract
Control Core ↔ Agent ต้องรองรับ:
- command request
- command acknowledgement
- command result
- policy update
- heartbeat
- state snapshot
- state-change event
- alarm event

Transport ต้อง replaceable โดย semantic contract ไม่เปลี่ยน

## Idempotency Rules
- SetHostEnabled(same value) = no harmful change
- SetInternetPolicy(same policy) = converge/no duplicate rules
- SetDatabasePolicy(same policy) = converge/no duplicate rules
- EnsurePortPolicy = desired-state convergence
- ApplyPolicy(same revision) = safe no-op/reconcile
- Maintenance enable/disable = repeat-safe

## Error Categories
อย่างน้อย:
- VALIDATION_ERROR
- PRIVILEGE_REQUIRED
- AUTHENTICATION_FAILED
- AUTHORIZATION_FAILED
- CONFIG_ERROR
- POLICY_CONFLICT
- POLICY_STALE
- AGENT_OFFLINE
- NETWORK_APPLY_FAILED
- NETWORK_VERIFY_FAILED
- FIREWALL_FAILED
- SQL_UNREACHABLE
- SCHEDULE_INVALID
- DRIFT_DETECTED
- ROLLBACK_FAILED
- UNKNOWN_ERROR
