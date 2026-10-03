# ADR-006 — Explicit State, Operation Stage and Control Cycle Model

- Status: Accepted
- Date: 2026-10-03

## Context
MTP6CoopNW is a control-oriented distributed system. Host state alone is insufficient to explain what the system is currently doing, which step a command has reached, whether it is safe to continue, and how the system recovers from failure.

## Decision
The platform shall model three different concepts explicitly:

1. **State** — durable operational condition of a host/subsystem.
2. **Stage** — progress of one operation or command.
3. **Cycle** — recurring control loop used by Agent/Core to observe, evaluate, reconcile, verify and publish.

### Host/Subsystem State
Baseline states:
- UNKNOWN
- STARTING
- NORMAL
- SCHEDULE_BLOCKED
- DISABLED
- MAINTENANCE
- WARNING
- FAULT
- RECOVERY
- OFFLINE

### Operation Stage
Baseline stages:
- REQUESTED
- VALIDATING
- PLANNING
- WAITING_APPROVAL
- APPLYING
- VERIFYING
- COMPLETED
- FAILED
- ROLLING_BACK
- ROLLED_BACK
- ROLLBACK_FAILED
- CANCELLED
- TIMED_OUT

### Control Cycle
Baseline loop:
Read Policy → Read Actual State → Evaluate Schedule → Resolve Effective Policy → Compare Desired/Actual → Check Interlocks → Reconcile → Verify → Publish Status → Audit/Alarm → Wait

### Timing
Fast and slow cycles are separate:
- Fast cycle: heartbeat, command result, critical state, policy revision
- Slow cycle: deeper diagnostics, drift, SQL/service/disk/backup checks

All intervals are configurable.

### Timeout
Every blocking stage must have a timeout policy. Timeout never silently becomes success.

## Consequences
- Better operator visibility
- Better auditability
- Easier automated testing
- Deterministic recovery paths
- Easier progress reporting in UI
- Additional state-machine implementation and test complexity

## Enforcement
UI, Core and Agent contracts must preserve the distinction between State, Stage and Cycle. UI may summarize them visually but must not collapse them into one ambiguous status field.
