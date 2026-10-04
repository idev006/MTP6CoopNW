# ADR-009 — Bounded Operation Stage, Cancellation and Rollback Contract

- Status: Accepted
- Date: 2026-10-04

## Context
MTP6CoopNW models state-changing work as explicit operation stages. Before M8 Planner/Dry Run and M9 enforcement, the lifecycle needs one deterministic contract for timeout, cancellation, verification and rollback so that UI, Core and Agent cannot disagree about whether an operation succeeded.

## Decision
1. Every state-changing operation has a unique operation ID and correlation ID.
2. Baseline stage sequence is:
   REQUESTED → VALIDATING → PLANNING → APPLYING → VERIFYING → COMPLETED
3. Failure path is:
   FAILED → ROLLING_BACK → ROLLED_BACK
   or ROLLBACK_FAILED when safe recovery cannot be verified.
4. Additional terminal states are CANCELLED and TIMED_OUT.
5. Each externally waiting stage has a configurable deadline. Exceeding the deadline is an explicit TIMED_OUT result, never implicit success.
6. Cancellation is accepted only at stages declared cancellable. APPLYING may reject cancellation when interruption could leave a partial unsafe state.
7. A plan records:
   - current state
   - desired state
   - intended changes
   - affected project-owned objects
   - interlocks
   - warnings
   - verification checks
   - rollback candidate
8. APPLYING is not successful until VERIFYING reads actual state and confirms the expected result.
9. Rollback also requires read-back verification. A rollback command being issued is not enough to mark ROLLED_BACK.
10. Repeated requests with the same operation ID must be idempotent and return the existing operation status rather than executing twice.
11. Core and Agent persist enough operation metadata to recover/report an interrupted operation after restart.
12. Audit events are emitted for every stage transition, timeout, cancellation request, failure and rollback result.
13. Emergency paths, if ever added, must be explicitly documented and cannot silently bypass verification/audit.

## Consequences

### Positive
- Prevents indefinite waiting and ambiguous success.
- Gives UI a stable progress model.
- Enables safe retry/restart behavior.
- Makes rollback evidence testable.
- Separates planning from execution.

### Trade-offs
- More state must be persisted.
- Some operations will need capability-specific rollback logic.
- Cancellation cannot be promised at every stage.

## Safety
No high-impact operation may report COMPLETED before post-change verification. If verification is inconclusive, the result is failure/timeout and recovery logic decides the next safe stage.

## Implementation Gate
M8 must implement this lifecycle using fake adapters before any M9 enforcement adapter is accepted.
