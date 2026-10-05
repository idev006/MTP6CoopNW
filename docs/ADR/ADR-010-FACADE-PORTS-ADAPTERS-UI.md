# ADR-010 — Facade, Ports/Adapters and Replaceable Presentation Layer

- Status: Accepted
- Date: 2026-10-04

## Context
MTP6CoopNW must support multiple presentation technologies over its lifetime: CLI, desktop UI, web dashboard, API clients and automated tests. Presentation code must not know how policy, host registries, persistence, transport or Windows-specific adapters are implemented.

The project already uses port interfaces for network, firewall, SQL, services, policy storage, audit, clock and transport. A stable application boundary is needed above the Core so UI code does not couple itself to internal services.

## Decision
1. Use an application **Facade** as the normal presentation entry point.
2. UI/CLI/Web depend on facade contracts, never directly on registries, Windows adapters or persistence.
3. Core business logic remains headless and UI-independent.
4. External dependencies remain behind small capability-focused Ports/Interfaces.
5. Infrastructure implementations use Adapter pattern.
6. Presentation code may depend on a narrow Protocol/interface representing only the use cases it needs.
7. Backward-compatible API names may remain as aliases while the architecture migrates to facade terminology.
8. Future state-changing operations will be exposed as use-case/Command contracts through the facade rather than arbitrary method access.
9. Cross-cutting concerns such as audit, metrics, timeout and retry should wrap boundaries rather than be embedded in UI logic.
10. Pattern use must remain pragmatic: introduce a pattern only when it reduces coupling, improves testability/safety, or enables replacement of an implementation.

## Baseline Layering

Presentation (CLI / Desktop / Web)
→ Facade / Application Contract
→ Core / Policy / State / Scheduler / Planner Engines
→ Ports / Interfaces
→ Adapters
→ Windows / SQL / Storage / Transport

## Consequences

### Positive
- UI can be replaced without rewriting the engine.
- Automated tests can substitute fake facades or fake ports.
- Core/Agent remain independently testable.
- Infrastructure changes do not leak into presentation code.
- Easier parallel development by UI, Core, Agent and adapter teams.

### Trade-offs
- One additional application boundary must be maintained.
- Facades must not grow into a god object; split by coherent use case when necessary.
- Compatibility aliases require eventual cleanup/versioning.

## Pattern Guidance
Preferred patterns when justified:
- Facade: presentation/application boundary
- Adapter: Windows/SQL/network/storage/transport
- Strategy: policy/scheduling/fail-safe variants
- State: durable host and operation lifecycle
- Command: planned state-changing operation
- Observer/Event: telemetry, alarms and audit propagation
- Repository: persistence abstraction
- Factory/Composition Root: environment-specific assembly
- Decorator: metrics/audit/timeout/retry around boundaries

Avoid pattern stacking without a concrete requirement.

## Test Rule
Every use case exposed to UI must be testable without launching the UI. Presentation tests may use a fake facade; engine tests use fake ports/adapters.
