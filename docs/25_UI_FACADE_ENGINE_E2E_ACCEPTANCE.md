# 25 — UI Facade → Engine End-to-End Acceptance

- Date: 2026-10-04
- Status: Engineering/Sandbox acceptance contract implemented
- Scope: headless functional UI testing before a concrete GUI toolkit exists

## Goal

Prove that UI intent can travel through the same application boundary that a concrete UI will use, execute real domain engines, publish operation/status events, and return presentation-ready state to the Presenter/ViewModel.

## Tested path

UI intent
→ NetworkControlFacade
→ authorization
→ EngineCommandExecutor
→ PolicyEngine
→ Planner
→ OperationEngine
→ read-back / rollback semantics
→ simulated Agent state report
→ ControlCore
→ InMemoryEventBus
→ UiEventGateway
→ UiApplicationFacade
→ DashboardPresenter
→ DashboardViewModel

The integration intentionally replaces only operating-system/network side effects with an in-memory MutableHost. Policy, planning, operation lifecycle, authorization, audit, event propagation, facade projection and presenter behavior are real project components.

## UI command scenarios

1. Host logical ON/OFF reaches Policy/Planner/Operation and returns to ViewModel.
2. Internet ON/OFF reaches the same engine path and returns to ViewModel.
3. Database access ON/OFF reaches the same engine path and returns to ViewModel.
4. Port configuration reaches engine state and returns allowed ports to ViewModel.
5. Verification failure rolls back and ViewModel receives the rolled-back state.
6. Viewer mutation is rejected before engine execution.
7. Mutation audit records actor and final operation result.
8. Operation stage events reach Presenter through UiApplicationFacade.
9. UNKNOWN health is fail-closed for canApply/canPlan presentation hints.
10. Existing snapshot, event replay, resync, freshness and operation-progress tests remain applicable.

## Important boundary

This proves concrete UI integration can bind to stable facades without duplicating domain logic.

It does not prove widget rendering, keyboard navigation, responsive layout, accessibility, or toolkit-specific click binding. Those are tested after a concrete UI framework exists.

It also does not replace controlled tests against real Windows Firewall, routes, SQL Server, Windows Service lifecycle and mTLS transport.
