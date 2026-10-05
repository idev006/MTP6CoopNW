# 22 — UI Facade and Automation Contract

- Status: ACTIVE
- Date: 2026-10-04

## Goal
Keep every concrete UI replaceable and automatically testable without launching Core, Agent, Windows, SQL or real network infrastructure.

## Boundary
Concrete UI → DashboardPresenter/ViewModel → DashboardBackend Protocol → UiApplicationFacade → Application/Core engines.

UI must not import Core registries, Windows adapters, SQL adapters, PowerShell bridges or policy internals.

## Contract
The UI bootstrap contract returns presentation-ready host cards, alarms, summary and latest event sequence.

The UI event contract returns ordered event deltas plus latestSequence and resyncRequired.

Action flags such as canPlan/canApply/canRetry are supplied by the application boundary as UI hints. The actual command path must always revalidate authorization, current state and safety interlocks; disabling a button is not a security control.

## Automated-test strategy
1. Engine tests use fake ports and clocks.
2. Facade contract tests prove stable UI-shaped payloads.
3. Presenter/ViewModel tests inject a FakeDashboardFacade and require no Engine.
4. Event tests drive freshness, telemetry, policy and operation stage transitions without a real UI toolkit.
5. Concrete toolkit tests should be limited to rendering, binding, navigation, keyboard/accessibility and click wiring.
6. Full end-to-end tests remain few and run against an integration environment.

## Reactive lifecycle
1. UI calls bootstrap_dashboard once.
2. UI renders DashboardViewModel.
3. UI waits for event deltas from latestSequence.
4. Presenter applies known events to the local view model.
5. Unknown event types are ignored for forward compatibility.
6. If resyncRequired is true, Presenter reloads a full snapshot.

## Rule
Business rules belong in engines/application services. The UI renders decisions and gathers intent; it must not become an alternative policy engine.
