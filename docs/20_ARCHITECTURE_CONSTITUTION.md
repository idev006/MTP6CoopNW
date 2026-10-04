# 20 — Architecture Constitution & Software Engineering Standards

- Status: ACCEPTED
- Date: 2026-10-04
- Authority: Normative project-wide engineering rule
- Related ADR: ADR-001, ADR-004, ADR-010, ADR-011, ADR-012
- Principle: Document First → Contract First → Implementation Second → Evidence Always

## 1. Purpose

This constitution defines non-negotiable architecture and software-engineering rules for MTP6CoopNW. It exists so humans and AI developers can change implementations without changing system meaning, safety rules, or testability.

When source code and this document disagree, the discrepancy must be resolved deliberately. Production behavior that contradicts accepted SSOT is a defect or an unapproved architecture change.

## 2. Canonical Layer Model

    Concrete UI / UX
    (Web / Desktop / CLI / future client)
            ↓
    Presenter / ViewModel
            ↓
    UI Facade
    (presentation-oriented contract)
            ↓
    Application Service APIs
    (programming interfaces; NOT synonymous with Web API)
            ↓
    Domain / Control Engines
    Policy / Scheduler / Planner / Operation /
    Reconciliation / Monitoring / Alarm
            ↓
    Ports
    Clock / Network / Firewall / SQL / Service /
    PolicyStore / AuditStore / Transport
            ↓
    Adapters
    Fake / In-memory / Windows / SQL / File / mTLS
            ↓
    Operating System / Network / SQL Server / Storage

Events travel upward through the same architectural boundaries:

    Engines / Core
        ↓ publish
    Application Event Bus
        ↓
    UI Event Gateway / Facade
        ↓
    Presenter / ViewModel
        ↓
    Concrete UI

## 3. Meaning of API in this Project

"API" means an Application Programming Interface or programming contract between components. It does not imply HTTP, REST, JSON, or a web server.

Examples:
- Policy service contract
- Planning service contract
- Operation service contract
- Monitoring query contract
- Command contract
- Event stream contract
- Repository/Port contract

HTTP/SSE/WebSocket may be transport mechanisms around these contracts, but transport must not define domain semantics.

## 4. Layer Responsibilities

### 4.1 Engines

Engines own business/control semantics.

They may:
- evaluate policy,
- evaluate schedules,
- classify state,
- create plans,
- enforce operation lifecycle,
- verify and roll back,
- detect/reconcile drift,
- evaluate alarms.

They must not:
- render UI,
- know widget/toolkit details,
- depend on HTTP frameworks,
- call arbitrary shell commands,
- directly own Windows-specific implementation details.

### 4.2 Application Service APIs

Application Service APIs expose coherent use cases of one or more engines.

They:
- provide typed/narrow contracts,
- orchestrate engines,
- preserve invariants,
- return structured results,
- publish application events,
- remain usable without any UI.

They are the stable programming surface above engines.

### 4.3 UI Facades

Facades adapt application services into presentation-ready operations and DTO/ViewModel projections.

They:
- aggregate data needed by screens,
- expose action availability hints,
- normalize errors/results for presentation,
- hide engine composition and infrastructure details,
- provide command/query operations required by UI.

They must not:
- duplicate domain policy,
- bypass authorization/interlocks,
- become a god object.

Split facades by coherent use case when scope grows.

### 4.4 Presenter / ViewModel

Presenter/ViewModel:
- converts facade DTOs/events into screen state,
- coordinates local presentation state,
- tracks operation progress,
- handles resync/reload behavior.

It must not decide business policy.

### 4.5 Concrete UI / UX

The concrete UI is a replaceable presentation shell — effectively a mask over tested application behavior.

It may:
- collect operator intent,
- display ViewModels,
- show confirmations,
- render progress/errors,
- navigate screens,
- handle accessibility and input.

It must not:
- implement schedule logic,
- calculate policy priority,
- decide authorization,
- call adapters,
- manipulate firewall/network/SQL directly.

A disabled button is never a security boundary. Backend/application services revalidate every command.

### 4.6 Ports and Adapters

All external side effects must cross a Port.

Production adapters implement the same contract as fake/test adapters.

Windows/PowerShell/SQL/file/transport implementation details belong outside domain engines.

## 5. Dependency Rule

Dependencies point inward toward stable contracts and domain semantics.

Allowed:

    UI → Facade Protocol
    Facade → Application Service Protocol
    Application Service → Engine Protocol
    Engine → Port Protocol
    Adapter → Port Protocol implementation

Forbidden:

    Engine → UI
    Engine → Windows implementation
    UI → Engine concrete class
    UI → Adapter
    Facade → PowerShell
    Domain → HTTP framework

Where practical, Facades and orchestrators depend on Protocol/interface contracts rather than concrete engine classes.

## 6. Mandatory Design Patterns

Patterns are tools, not goals. Use them only where they reduce coupling, improve safety/testability, or enable replacement.

Project-approved patterns:
- Facade — UI/application boundary
- Ports & Adapters / Hexagonal — infrastructure boundary
- Strategy — policy/scheduling/fail-safe variants
- State — host and operation lifecycle
- Command — planned state-changing operations
- Observer/Event — telemetry, alarms, UI updates
- Repository — persistence abstraction
- Dependency Injection — testing and environment composition
- Composition Root — the only place that assembles concrete implementations
- Decorator — audit/metrics/timeout/retry when appropriate
- Specification — reusable policy/interlock predicates when complexity justifies it

Avoid meaningless chains such as Facade → Manager → Coordinator → Handler → Service when layers add no distinct responsibility.

## 7. Contract Standards

1. Stable cross-layer contracts should be typed.
2. Prefer dataclass/TypedDict/domain DTO/Protocol over broad dict[str, Any].
3. dict[str, Any] is acceptable at serialization/plugin boundaries, not as the long-term internal architecture default.
4. Contract fields must have stable names and explicit optionality.
5. Version externally persisted or transmitted schemas.
6. Errors must be structured and classifiable.
7. Time-dependent logic must use ClockPort/FakeClock.
8. State-changing commands must carry correlation/operation identity.
9. Duplicate/replayed commands must be safe and idempotent.
10. Secrets must never be part of ordinary DTO/log output.

## 8. Command / Query Separation

Queries:
- read state,
- do not cause hidden mutations,
- are safe to repeat.

Commands:
- express operator intent,
- require authorization,
- validate safety/interlocks,
- create operation identity,
- support plan/verify/rollback as applicable,
- emit audit and events.

UI code must never turn a query into an implicit mutation.

## 9. Safety Rules for State Change

Every applicable destructive/state-changing use case follows:

    Intent
    → Authorize
    → Validate
    → Plan / Dry Run
    → Safety Interlock
    → Apply
    → Read Back
    → Verify
    → Publish
    → Audit

Failure path:

    FAILED
    → ROLLING_BACK
    → ROLLED_BACK / ROLLBACK_FAILED

No UI or adapter may bypass this lifecycle unless a separately accepted emergency ADR explicitly permits it.

## 10. Event-Driven Presentation

UI loads one authoritative snapshot and then consumes application events.

Rules:
- events are deltas, not a second authority,
- sequence numbers are monotonic within a stream,
- reconnect replays when retention permits,
- replay gap requires snapshot resync,
- commands continue through command/application APIs,
- UI does not poll merely to manufacture state transitions.

Periodic reconciliation remains mandatory even when event push exists.

## 11. Automated Testing by Layer

Every layer must be independently testable.

### L0 — Pure Domain Unit
Policy, schedule, state, planner, drift, interlock.

### L1 — Engine Contract
Engine behavior through protocols with fake ports.

### L2 — Application Service
Use-case orchestration without UI.

### L3 — Facade Contract
Presentation DTOs, permissions, action hints, error mapping.

### L4 — Facade → Engine Functional E2E
UI intent → Facade → real domain engines → fake adapters → events → UI Facade → Presenter/ViewModel.

### L5 — Adapter Contract
Production adapter behavior against mocks or controlled systems.

### L6 — Concrete UI
Rendering, binding, navigation, accessibility, keyboard/mouse/touch behavior.

### L7 — Controlled Real-World Acceptance
Windows Firewall, routing, SQL Server, Windows Service, mTLS, restart/recovery, site topology.

A feature touching operating-system/network/SQL state is not production-proven until L7 passes.

## 12. UI as Replaceable Mask

The UI is intentionally replaceable.

A correct implementation must permit:
- Desktop UI replacement by Web UI,
- CLI automation using the same application services,
- headless automated testing,
- future mobile/read-only clients,
without rewriting policy or operation engines.

If changing UI technology requires changing policy semantics, architecture boundaries have failed.

## 13. Definition of Done — Architecture

A use case is engineering-complete only when applicable items exist:
- SSOT requirement/use-case entry,
- stable contract,
- engine/application implementation,
- facade exposure if user-facing,
- automated unit/contract/scenario evidence,
- failure-path evidence,
- observable events/state,
- audit for mutation,
- real integration acceptance where external side effects exist.

## 14. Architecture Review Checklist

Before merge:
- Does UI import engine or adapter internals?
- Does Facade contain domain policy?
- Is a concrete engine dependency avoidable through a Protocol?
- Is external I/O behind a Port?
- Can the use case run headlessly?
- Can time be controlled with FakeClock?
- Can failure/rollback be simulated?
- Is the result structured and typed?
- Are authorization and safety enforced below UI?
- Are events/audit emitted?
- Is there a traceable test/evidence path?
- Has the Project Book/ADR been updated if architecture changed?

Any "yes" to a forbidden dependency or "no" to a mandatory safety/testability item blocks acceptance unless explicitly waived by ADR.
