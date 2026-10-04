# 26 — Layer Readiness Matrix

- Status: ACTIVE SSOT
- Date: 2026-10-04
- Scope: Architecture, engineering/sandbox, integration, and production readiness by layer
- Related: 20_ARCHITECTURE_CONSTITUTION.md, ADR-012, 23_MASTER_USE_CASE_CAPABILITY_MATRIX.md, 25_UI_FACADE_ENGINE_E2E_ACCEPTANCE.md
- Rule: A layer may be architecturally complete without being production-ready.

## 1. Purpose

This document prevents the project from using a single ambiguous word such as "complete" for different maturity levels.

Every architectural layer is tracked across four independent gates:

- **A — Architecture Complete**: boundary, responsibility, dependency direction, and contract are defined.
- **S — Sandbox Complete**: implementation can be exercised headlessly with fake/in-memory dependencies.
- **I — Integration Complete**: verified against its real adjacent dependency or real platform boundary.
- **P — Production Ready**: operational, security, recovery, packaging, observability, and acceptance gates are satisfied.

## 2. Canonical Layers

    LAYER 1  Concrete UI / UX
        ↓
    LAYER 2  Presenter / ViewModel
        ↓
    LAYER 3  UI Facade
        ↓
    LAYER 4  Application Service APIs
        ↓
    LAYER 5  Domain / Control Engines
        ↓
    LAYER 6  Ports / Interfaces
        ↓
    LAYER 7  Adapters
        ↓
    LAYER 8  Infrastructure / OS / Network / SQL

Upward asynchronous flow:

    Infrastructure / Agent / Engines
        → Core / Event Bus
        → Event Gateway / UI Facade
        → Presenter / ViewModel
        → Concrete UI

## 3. Readiness Matrix

| Layer | Primary responsibility | A | S | I | P | Current evidence / note |
|---|---|:---:|:---:|:---:|:---:|---|
| 1. Concrete UI / UX | Rendering, input, navigation, accessibility | ✅ | ⚠️ | ❌ | ❌ | Headless UI contract exists; concrete production GUI/toolkit is not yet the acceptance target. |
| 2. Presenter / ViewModel | Presentation state, event application, resync, operation progress | ✅ | ✅ | ⚠️ | ❌ | DashboardPresenter/ViewModels and fake-facade tests exist; concrete GUI binding remains pending. |
| 3. UI Facade | Presentation-ready queries/commands/DTO projection | ✅ | ✅ | ⚠️ | ❌ | UiApplicationFacade, NetworkControlFacade, typed payloads, event gateway path exist; real UI binding pending. |
| 4. Application Service APIs | Stable use-case programming contracts above engines | ✅ | ✅ | ⚠️ | ❌ | Protocol contracts and EngineCommandExecutor exist; production runtime integration still depends on real adapters/transport. |
| 5. Domain / Control Engines | Policy, schedule, planning, operation, reconciliation, monitoring/alarm semantics | ✅ | ✅ | ⚠️ | ❌ | Sandbox/reference behavior and use-case evidence exist; real external side effects are intentionally outside this layer. |
| 6. Ports / Interfaces | Technology-neutral external dependency contracts | ✅ | ✅ | ⚠️ | ❌ | Clock/Network/Firewall/SQL/Service/Store/Transport contracts exist; each real adapter must prove conformance. |
| 7. Adapters | Fake and production implementations for external effects | ✅ | ✅ | ⚠️ | ❌ | Fake/in-memory and read-only foundations exist; destructive Windows/SQL/network and real mTLS acceptance remain pending. |
| 8. Infrastructure / OS / Network / SQL | Real Windows hosts, firewall, routes, SQL Server, services, certificates, topology | ✅ | N/A | ❌ | ❌ | Baseline topology documented; controlled real-site integration and recovery tests not yet completed. |

Legend:
- ✅ gate satisfied for current scope
- ⚠️ partially satisfied / adjacent integration exists but real-world proof remains
- ❌ not yet satisfied
- N/A not a sandbox software layer

## 4. Architecture Completion

All 8 canonical layers are defined with explicit responsibility and dependency direction.

**Architecture-layer definition: 8/8 = 100%.**

This does **not** mean all 8 layers are production-ready.

## 5. Engineering / Sandbox Interpretation

Layers 2–7 have executable/headless implementation paths. Layer 1 is represented by a stable UI contract plus Presenter/ViewModel but the concrete GUI remains intentionally replaceable. Layer 8 is a real-world environment, not something that can be completed purely in sandbox.

Current engineering statement:

- Core architecture and headless application path: COMPLETE for sandbox scope.
- Concrete GUI mechanics: PENDING.
- Real destructive Windows/Firewall/Route/SQL adapters: CONTROLLED INTEGRATION PENDING.
- Real mTLS/certificate lifecycle: CONTROLLED INTEGRATION PENDING.
- Real restart/recovery/site-topology acceptance: PENDING.
- GitHub runner execution at current branch head: NOT VERIFIED while jobs report runner_id=0 / no steps.

## 6. Required Evidence by Layer

### Layer 1 — Concrete UI / UX
Production gate requires:
- widget/action binding,
- navigation,
- validation/error display,
- confirmation for high-impact operations,
- keyboard/touch behavior as applicable,
- accessibility,
- responsive/layout acceptance,
- no business logic duplicated in UI.

### Layer 2 — Presenter / ViewModel
Requires:
- fake-facade tests,
- snapshot load,
- event delta application,
- operation progress,
- replay-gap resync,
- unknown event forward compatibility.

### Layer 3 — UI Facade
Requires:
- typed presentation DTOs,
- command/query separation,
- fail-closed action hints,
- no concrete Engine/Adapter imports,
- facade contract tests.

### Layer 4 — Application Service APIs
Requires:
- narrow Protocol/interface contracts,
- typed internal results,
- authorization/interlock below presentation,
- headless execution,
- stable use-case semantics.

### Layer 5 — Domain / Control Engines
Requires:
- deterministic policy resolution,
- FakeClock schedule coverage,
- planning/interlocks,
- bounded apply/verify/rollback,
- drift/reconciliation,
- monitoring/alarm semantics,
- failure-path tests.

### Layer 6 — Ports / Interfaces
Requires:
- replaceable contracts,
- fake implementations,
- production adapter conformance,
- timeout/error semantics.

### Layer 7 — Adapters
Requires:
- mocked/contract tests,
- controlled Windows/SQL integration,
- project-owned mutation boundary,
- idempotency,
- read-back verification,
- rollback/recovery.

### Layer 8 — Infrastructure / OS / Network / SQL
Requires:
- verified site topology,
- Windows Firewall behavior,
- route/control-path safety,
- SQL reachability and WAN denial,
- Windows Service lifecycle,
- mTLS certificate identity/rotation/revocation,
- restart/outage/recovery tests,
- operational evidence.

## 7. Promotion Rule

No layer may be promoted from S → I or I → P by documentation alone.

Promotion requires executable evidence at the corresponding boundary.

In particular:
- a fake adapter passing tests cannot promote the production adapter to Integration Complete;
- a Facade-to-Engine sandbox test cannot promote Windows Firewall or SQL behavior to Production Ready;
- a rendered UI cannot compensate for missing engine/application evidence.

## 8. Release Gate

The system is eligible for production release only when:

1. all applicable layers are Architecture Complete,
2. all software layers are Sandbox Complete,
3. production adapters and infrastructure are Integration Complete,
4. mandatory real-world acceptance scenarios in the Master Use Case Matrix pass,
5. security/recovery/rollback evidence is recorded,
6. CI/release evidence is available from an executing runner or an approved equivalent controlled test environment.

## 9. Current Project Readiness Statement

As of 2026-10-04:

- **Architecture definition:** 100%.
- **Headless/sandbox architecture path:** complete for current engineering scope.
- **Concrete GUI production acceptance:** pending.
- **Real Windows/SQL/network/mTLS integration:** pending.
- **Production readiness:** not yet declared.

This matrix is the authority whenever a progress report uses the words "complete", "ready", or "done".
