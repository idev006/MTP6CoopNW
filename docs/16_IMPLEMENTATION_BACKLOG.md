# 16 — Implementation Backlog & Build Order

- Status: ACCEPTED
- Purpose: แปลง Implementation Plan ให้เป็นลำดับงานที่ทีมสามารถหยิบไปพัฒนาได้ทันที โดยลดความเสี่ยงจาก Windows/network side effects

## 1. Build Strategy

หลักลำดับการสร้าง:

```text
Contracts
  ↓
Config
  ↓
Fake Adapters
  ↓
Observability
  ↓
Read-only Adapters
  ↓
Read-only Agent
  ↓
Control Core
  ↓
Policy/Scheduler
  ↓
Dry-run Planner
  ↓
Real Enforcement
  ↓
Reconciliation/Drift
  ↓
Application Service APIs
  ↓
UI Facades / Presenter / ViewModel
  ↓
Central Control UI
  ↓
Packaging/Rollout
```

ห้ามเริ่ม destructive adapter ก่อน Fake/Read-only/Contract tests พร้อม

## 2. Milestone M0 — Repository Bootstrap

Deliverables:
- `pyproject.toml`
- source layout
- tests layout
- PowerShell module layout
- config examples
- schemas folder
- scripts folder
- GitHub Actions baseline
- .gitignore
- developer commands

Quality Gate:
- clean checkout สามารถติดตั้ง development dependencies ได้
- unit test command ทำงานแม้ยังไม่มี Windows mutation
- TOML example validation ผ่าน

## 3. Milestone M1 — Contracts & Configuration

### Tasks
- Define Result model
- Define Error model
- Define HostStatus
- Define Policy model
- Define Alarm model
- Define Command/Event envelopes
- Define adapter interfaces
- TOML loader
- environment/site overlay strategy
- config validation
- schemaVersion/policyRevision

### Tests
- valid config
- invalid config
- unknown key
- missing required field
- timezone validation
- port range validation
- duplicate schedule validation
- stable serialization

### Exit
Core logic can load config/policy without importing Windows-specific code.

## 4. Milestone M2 — Fake Runtime & Simulation

### Fake Components
- FakeClock
- FakeNetworkAdapter
- FakeFirewallAdapter
- FakeSqlAdapter
- FakeServiceAdapter
- FakeTransport
- InMemoryPolicyStore
- InMemoryAuditStore

### Simulation Scenarios
- Client normal
- Client schedule blocked
- Internet blocked
- DB blocked
- port blocked
- agent offline
- policy drift
- SQL unavailable
- DB server maintenance

### Exit
Use cases can be exercised end-to-end in memory.

## 5. Milestone M3 — Observability Foundation

### Deliverables
- structured JSON logger
- correlation ID
- operation timer
- health model
- readiness/liveness model
- metric registry abstraction
- audit event model
- stale/offline detection
- redaction helper

### Required Events
- agent.started
- agent.heartbeat
- policy.received
- policy.applied
- reconcile.started
- reconcile.completed
- drift.detected
- command.started
- command.completed
- alarm.raised
- alarm.cleared

### Exit
Every simulation produces readable structured status and logs.

## 6. Milestone M4 — Read-Only PowerShell Adapters

### MTP6.Network
- Get-MTP6NetworkState
- Test-MTP6LanReachability
- Test-MTP6InternetReachability
- Get-MTP6Routes

### MTP6.Firewall
- Get-MTP6ManagedFirewallState
- Test-MTP6FirewallDrift

### MTP6.Services
- Get-MTP6ServiceState

### MTP6.Sql
- Test-MTP6SqlTcp
- Get-MTP6SqlServiceState

### Contract
PowerShell returns objects serialized by adapter boundary; presentation output forbidden.

### Tests
- Pester mocks
- result shape
- timeout/failure mapping
- no mutation assertion

## 7. Milestone M5 — Read-Only Local Agent

### Agent Loop
1. load config
2. validate identity
3. load last-known policy
4. adapter self-test
5. collect status
6. send heartbeat
7. reconcile read-only
8. repeat

### Exit
Agent can run as console/service candidate and report status without changing Windows state.

## 8. Milestone M6 — Central Core & Single Point Monitoring

### Core Services
- HostRegistry
- StateRegistry
- PolicyRegistry
- CommandService
- TelemetryIngest
- AlarmService
- AuditService

### Central API
Minimum:
- list hosts
- get host status
- get alarms
- get policy
- agent register
- heartbeat ingest
- state event ingest

### Minimal Operator Console
Before full GUI, provide one central read-only console/dashboard showing all hosts.

### Exit
All managed hosts can be monitored from one point.

## 9. Milestone M7 — Policy & Scheduler

### Policy Resolution
Priority:
1. critical/safety
2. emergency disable
3. manual override
4. maintenance
5. schedule
6. default

### Scheduler
- timezone-aware
- FakeClock tested
- next transition calculation
- restart recovery
- Core disconnected behavior

### Exit
Effective policy can be calculated deterministically for every host/time.

## 10. Milestone M8 — Planner / Dry Run

Every state-changing action first produces:

```text
Current
Desired
Planned changes
Managed objects affected
Interlocks
Warnings
Verification steps
Rollback candidate
```

API concept:
- plan_command()
- apply_plan(plan_id)
- verify_operation()
- rollback_operation()

### Exit
No destructive action can bypass planning contract except explicitly documented emergency paths.

## 11. Milestone M9 — Enforcement Adapters

Implement one capability at a time:

### E1 — Project-Owned Firewall Rule Management
First destructive capability because ownership boundary is clear.

### E2 — Database Access
Allow/Deny Client → DB Server TCP according to policy.

### E3 — General Port Policy
TCP/UDP rules.

### E4 — Client Internet Access
Implement while preserving control-plane/LAN requirements.

### E5 — DB Server Maintenance Internet
Temporary route/gateway/firewall changes with strict verification.

For each:
- plan
- apply
- read back
- verify
- rollback
- idempotency
- Pester
- Windows integration test
- scenario acceptance

## 12. Milestone M10 — Reconciliation & Drift

Loop:
- read desired
- read actual
- compare
- classify difference
- auto-converge only approved changes
- otherwise alarm
- verify
- audit

### Drift Classes
- benign
- recoverable
- conflict
- unsafe
- unknown

## 13. Milestone M11 — Central User-Friendly Control UI

Minimum screens:
1. Overview
2. Host Detail
3. Policy/Schedule
4. Internet/DB/Port Control
5. Alarm Center
6. Diagnostics
7. Maintenance
8. Audit/History
9. Settings/System Health

UX:
- no raw PowerShell
- impact preview
- explicit Desired/Actual/Effective
- state freshness
- confirmation for high-impact actions
- clear rollback/recovery result

## 14. Milestone M12 — Packaging & Operations

- Python package/app bundle
- Windows Agent service installer
- PowerShell modules installation
- config bootstrap
- upgrade
- uninstall
- rollback
- log/data paths
- service recovery options
- version/status command
- diagnostics bundle

## 15. Mandatory Automated Checks Before Merge

Python:
- formatting/lint
- type checking
- unit
- contract
- scenario

PowerShell:
- syntax/static analysis
- Pester

Repository:
- TOML validation
- schema validation
- docs link check
- no secrets
- no generated/runtime artifacts committed

Windows protected runner:
- integration tests only when explicitly enabled

## 16. First Coding Increment

The first source-code increment shall contain only:
- repository skeleton
- config loader/validator
- contracts/models
- fake adapters
- structured logging
- unit tests
- CI

It must NOT change Windows Firewall, routes, IP configuration or SQL settings.

This increment proves architecture and testability before system mutation begins.

## 17. Architecture Hardening Gate

ก่อน concrete UI ถือว่าพร้อม ต้องมี:
- capability-oriented Engine/Application Service contracts
- UI Facade contracts
- Presenter/ViewModel contract
- Facade → Engine headless E2E tests
- fake adapters สำหรับ external side effects
- typed DTO migration plan
- Composition Root ที่รวม concrete implementations
- architecture dependency checks

UI implementation เป็นขั้น presentation หลัง business behavior ผ่าน headless tests แล้ว ไม่ใช่สถานที่สร้าง business rules.
