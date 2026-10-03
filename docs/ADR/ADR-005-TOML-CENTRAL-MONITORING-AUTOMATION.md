# ADR-005 — TOML-First Configuration, Central Monitoring and Automation-Friendly Design

- Status: Accepted
- Date: 2026-10-03

## Context
The system must be easy to configure, centrally controlled, centrally monitored, friendly to automated testing, and extensible without embedding operational knowledge in UI or hard-coded scripts.

## Decision
1. Human-editable configuration baseline is TOML.
2. Central Control Core provides the authoritative single-point management interface.
3. Operators perform normal configuration, control, monitoring and diagnostics from one central console/dashboard.
4. Local Agents continue enforcement and telemetry without requiring the UI to remain open.
5. All components expose structured health/status.
6. All state-changing capabilities must be invocable via programmatic contracts, not UI-only actions.
7. Business/process logic depends on interfaces so fake adapters and fake clocks can be used in automated tests.
8. Windows-specific side effects stay behind PowerShell adapter modules.
9. Structured logging, correlation IDs, health state and telemetry are default platform capabilities.
10. State-changing operations should support plan/dry-run where practical.

## Consequences

### Positive
- easier site configuration
- easier central operations
- better user experience
- high automated-test coverage without Windows mutation
- simpler monitoring and troubleshooting
- UI remains replaceable
- lower operational dependence on manual remote administration

### Trade-offs
- requires config schema/version discipline
- central Core becomes an important operational component
- local Agent fail-safe behavior must be well tested
- observability and test infrastructure must be implemented early, not postponed

## UX Constraint
The central UI must never become the source of business logic. It renders state and invokes Control Core contracts only.

## Safety Constraint
Loss of the central UI must not silently remove security or access policy. Agents retain last-known valid policy according to documented fail-safe behavior.
