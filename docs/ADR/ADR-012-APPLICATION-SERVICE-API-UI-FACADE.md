# ADR-012 — Application Service APIs, UI Facades and Headless Testability

- Status: Accepted
- Date: 2026-10-04
- Supersedes: none
- Related: ADR-001, ADR-010, ADR-011

## Context

MTP6CoopNW exposes capabilities from domain/control engines to multiple potential presentation technologies. The project uses the word API in the general software-engineering sense: a programming contract between components, not necessarily an HTTP/Web API.

Without a strict boundary, presentation code can accidentally depend directly on concrete engines or infrastructure, duplicate business rules, and become difficult to automate-test.

## Decision

1. Domain/control engines expose capability-oriented programming contracts.
2. Application Services orchestrate those engine APIs into complete use cases.
3. UI-facing Facades consume Application Service contracts and expose presentation-ready commands, queries and DTOs.
4. Presenter/ViewModel consumes Facade contracts.
5. Concrete UI consumes Presenter/ViewModel only and remains replaceable.
6. UI must not directly call concrete engine classes, persistence, Windows/PowerShell, SQL, firewall, transport or other adapters.
7. Facades must not duplicate domain policy. They may project/aggregate state for presentation and expose action hints.
8. Authorization, validation, interlocks and destructive-operation safety are revalidated below UI.
9. Application Service/Facade dependencies should use narrow Protocol/interfaces where practical rather than concrete engine classes.
10. Cross-layer contracts should migrate toward explicit typed DTOs rather than broad dict[str, Any].
11. Every UI-visible use case must be executable headlessly through Facade/Application contracts.
12. UI functional acceptance must include a Facade → Engine → Fake Adapter → Event → Facade → Presenter/ViewModel path.
13. Concrete GUI tests are a separate layer for rendering, binding, navigation and accessibility.
14. Network/SQL/Windows production acceptance remains a separate controlled integration gate.

## Canonical Direction

    Concrete UI
    → Presenter/ViewModel
    → UI Facade
    → Application Service API
    → Domain Engines
    → Ports
    → Adapters

Upward event flow:

    Domain/Core
    → Event Bus
    → Event Gateway / UI Facade
    → Presenter/ViewModel
    → Concrete UI

## Consequences

### Positive
- UI is effectively a replaceable mask over tested behavior.
- Most UI business behavior can be automated before choosing a concrete GUI toolkit.
- Engine and infrastructure layers can be tested independently.
- Desktop/Web/CLI can share the same use-case semantics.
- Failure location is easier to identify by layer.
- Infrastructure changes do not redefine domain logic.

### Trade-offs
- Stable contracts require deliberate versioning and maintenance.
- Extra DTO/protocol definitions add small upfront cost.
- Composition must be explicit.
- Teams must resist putting "convenient" policy logic in presentation code.

## Enforcement

Architecture review and automated tests should reject:
- UI imports of adapter/infrastructure modules,
- domain imports of UI or web frameworks,
- state-changing UI paths that bypass command/application services,
- untyped/broad contracts becoming de facto public interfaces without review.

The detailed normative rules are maintained in docs/20_ARCHITECTURE_CONSTITUTION.md.
