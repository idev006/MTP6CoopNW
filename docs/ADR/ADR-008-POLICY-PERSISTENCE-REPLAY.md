# ADR-008 — Versioned Policy Persistence and Replay Semantics

- Status: Accepted
- Date: 2026-10-04

## Context
M6 currently proves central monitoring with an in-memory `PolicyRegistry`. M7 introduces real policy and scheduling semantics. A production policy system must survive Core/Agent restarts, reject stale updates and reconcile desired state deterministically.

## Decision
1. Core is the authoritative source of desired policy; Agents retain only validated last-known policy needed for safe operation.
2. Every policy has:
   - schema version
   - monotonically increasing policy revision per managed scope/host
   - target host/scope
   - effective time
   - deterministic canonical content/hash
3. Core persists accepted policy revisions in durable storage before reporting them committed.
4. Agent policy cache writes are atomic and only occur after schema/semantic validation.
5. An Agent applies a policy only when its revision is newer than the currently accepted revision, except an explicitly modelled recovery/rollback revision issued by Core.
6. Duplicate delivery of the same revision and content is idempotent.
7. Same revision with different content is a conflict and must be rejected/alarmed.
8. Older unexpected revisions are rejected as stale and audited.
9. After restart/reconnect:
   - Agent loads last-known valid policy.
   - Agent reports current accepted revision/hash.
   - Core compares authoritative revision/hash.
   - Missing/newer policy is replayed through the authenticated transport.
10. Policy distribution and policy enforcement are separate stages. Receipt does not mean applied; the Agent must report validation/apply status.
11. No Agent may silently fall back to permissive defaults merely because Core is offline or a new policy is invalid.
12. Policy persistence must not contain credentials/secrets that belong in a dedicated secret mechanism.

## Consequences

### Positive
- Deterministic restart/reconnect behavior.
- Safe duplicate delivery and bounded replay.
- Clear auditability of desired versus accepted/applied revision.
- Supports future drift detection and rollback planning.

### Trade-offs
- Requires durable Core storage rather than the M6 in-memory registry.
- Requires migration/version handling as policy schema evolves.
- Rollback must be represented explicitly rather than by silently decrementing revision.

## Safety
The last-known valid policy remains active when a newer policy cannot be validated, authenticated or applied. Failure is surfaced as health/alarm state and never treated as success.

## Implementation Gate
M7 must implement and test revision comparison, duplicate/conflict behavior, restart recovery and fake persistence before M8 planner/dry-run is considered ready.
