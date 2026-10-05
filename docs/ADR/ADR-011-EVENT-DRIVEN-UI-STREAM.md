# ADR-011 — Event-Driven UI Stream

- Status: Accepted
- Date: 2026-10-04

## Context
The control dashboard must react quickly to host, alarm, policy and operation changes without repeatedly polling the full Core status. Polling wastes work, increases latency, and couples UI refresh frequency to infrastructure load.

## Decision
Use a hybrid snapshot-plus-events model.

1. UI bootstraps from a current snapshot through the Facade.
2. Core/Application/Operation engines publish versioned application events.
3. Events have eventId, monotonically increasing sequence, eventType, timestamp, source and optional host/operation/correlation/policy identifiers.
4. UI receives deltas through a streaming gateway. Server-Sent Events is the baseline one-way UI transport; WebSocket may be added only when bidirectional streaming is justified.
5. Commands remain on authenticated command/API paths; the event stream is not an arbitrary command channel.
6. The Core monitoring cycle, not the UI, produces time-driven freshness transitions such as ONLINE → STALE → OFFLINE.
7. A bounded replay buffer supports short reconnects. If the requested sequence is older than retained history, the gateway emits resync-required and the UI reloads a full snapshot.
8. Keepalive frames may be sent by the stream without forcing full-status polling.
9. Domain algorithms that benefit from purity may remain side-effect free; their application boundary publishes the outcome event.
10. Event streaming is additive to audit persistence. In-memory event replay is not the durable audit store.

## Event families
- host.registered
- host.telemetry_updated
- host.telemetry_duplicate
- host.telemetry_rejected
- host.freshness_changed
- policy.staged
- policy.evaluated
- operation.plan_created
- operation.stage_changed
- drift.detected
- drift.reconciled
- alarm.raised / alarm.cleared (when alarm lifecycle persistence is introduced)

## UI flow

Initial connection:
Facade snapshot → latestSequence → SSE stream from latestSequence.

Normal operation:
Engine → Event Bus → SSE Gateway → UI state update.

Reconnect:
Resume from last received sequence. If replay gap exists, bootstrap a new snapshot and reconnect.

## Consequences
Positive:
- no fixed-interval full-dashboard polling
- lower UI latency
- clear UI integration contract
- operation progress can be rendered immediately
- supports replaceable desktop/web/mobile presentation layers

Trade-offs:
- event ordering and reconnect semantics become part of the contract
- event retention is bounded
- production transport still needs authentication, authorization and connection limits
- durable event/audit storage remains a separate responsibility
