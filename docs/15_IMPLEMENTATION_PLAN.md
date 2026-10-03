# 15 — Implementation Plan, Configuration, Monitoring & Testability

- Status: ACCEPTED
- Owner: Senior Software Engineer
- Reviewers: Senior Network Engineer, Senior Process Engineer
- Related ADR: ADR-003, ADR-004, ADR-005
- Purpose: กำหนดวิธี implement source code และ scripts ให้ configure ง่าย, monitor ง่าย, test-friendly, automation-first และควบคุมจากจุดเดียว

## 1. Engineering Principles

### 1.1 Single Point of Control / Single Pane of Glass
ระบบต้องรองรับการตั้งค่า ควบคุม มอนิเตอร์ และตรวจสอบสถานะจากศูนย์กลางเพียงจุดเดียวสำหรับงานประจำวัน

ศูนย์กลางต้องสามารถ:
- ดูสถานะทุก host
- ดู online/offline/heartbeat
- ดู effective policy
- แก้ schedule
- Enable/Disable host
- Allow/Deny Internet
- Allow/Deny Database
- จัดการ port policy
- ดู alarm/warning/fault
- ดู policy drift
- สั่ง diagnostics
- ดูผล command ล่าสุด
- ดู audit/history
- ดู DB Server maintenance state

หลักสำคัญ:
- UI ส่วนกลางเป็น operator console
- Control Core เป็น authority
- Agent เป็น enforcement
- PowerShell Adapter เป็น low-level actuator
- ผู้ใช้ไม่ควรต้อง remote เข้าแต่ละเครื่องเพื่อทำงานประจำวัน

### 1.2 User Friendly by Design
UI/CLI ต้องแสดง desired state และ actual state แยกกันชัดเจน
ทุก action ที่มีความเสี่ยงต้อง:
- บอกผลกระทบ
- แสดง plan ก่อน apply เมื่อเหมาะสม
- แสดง progress/state
- แสดง success/failure แบบเข้าใจง่าย
- มี technical details ให้เปิดดูเพิ่มเติมได้
- มี next safe action/recovery guidance

### 1.3 Configuration First
ค่าที่เปลี่ยนตาม site/policy ห้าม hard-code

ใช้ TOML เป็น human-editable configuration baseline:
- อ่านง่าย
- รองรับ comment
- review diff ใน Git ง่าย
- แยก section ได้ชัด
- Python 3.11+ อ่านได้ด้วย standard library tomllib

### 1.4 Monitoring by Default
ทุก service/module ต้องตอบได้ว่า:
- healthy หรือไม่
- version
- policy revision
- last heartbeat
- last successful operation
- last error
- dependencies พร้อม/ไม่พร้อม

### 1.5 Test-Friendly Architecture
Business logic ต้องแยกจาก Windows side effects

Core tests ต้องใช้ FakeClock, FakeTransport, FakeNetworkAdapter, FakeFirewallAdapter, FakeSqlAdapter และ InMemoryPolicyStore ได้โดยไม่แก้ Windows จริง

### 1.6 Automation First
ทุก capability ที่ UI ทำได้ต้องมี programmatic contract
ห้ามมีความสามารถที่มีเฉพาะปุ่ม UI

### 1.7 Desired-State over Imperative Scripts
Core ระบุ desired state; Agent/Adapter converge actual state ไปหา desired state

### 1.8 Safe Dry Run
state-changing operation ควรรองรับ plan/dry-run เพื่อ preview current state, desired state, changes, risks และ validation result

## 2. Proposed Repository Structure

```text
MTP6CoopNW/
├─ pyproject.toml
├─ README.md
├─ config/
│  ├─ core.example.toml
│  ├─ agent.example.toml
│  ├─ policy.example.toml
│  └─ logging.example.toml
├─ src/
│  └─ mtp6coopnw/
│     ├─ contracts/
│     ├─ config/
│     ├─ core/
│     │  ├─ policy/
│     │  ├─ state/
│     │  ├─ scheduler/
│     │  ├─ alarms/
│     │  └─ commands/
│     ├─ agent/
│     │  ├─ runtime/
│     │  ├─ reconciliation/
│     │  └─ telemetry/
│     ├─ modules/
│     ├─ adapters/
│     │  ├─ interfaces/
│     │  ├─ fake/
│     │  └─ windows/
│     ├─ observability/
│     ├─ persistence/
│     └─ api/
├─ powershell/
│  ├─ MTP6.Network/
│  ├─ MTP6.Firewall/
│  ├─ MTP6.Services/
│  └─ MTP6.Sql/
├─ tests/
│  ├─ unit/
│  ├─ contract/
│  ├─ integration/
│  ├─ scenario/
│  └─ fixtures/
├─ scripts/
│  ├─ dev/
│  ├─ test/
│  ├─ package/
│  └─ install/
├─ schemas/
├─ docs/
└─ .github/workflows/
```

## 3. TOML Configuration Model

### 3.1 Core Config Example

```toml
[core]
node_id = "MTP6-CTRL-01"
timezone = "Asia/Bangkok"

[telemetry]
heartbeat_seconds = 3
stale_after_seconds = 10
offline_after_seconds = 30

[transport]
mode = "https"
bind = "0.0.0.0"
port = 8443

[logging]
level = "INFO"
format = "json"
```

### 3.2 Agent Config Example

```toml
[agent]
host_id = "CLIENT-01"
role = "client"
reconcile_seconds = 5

[core]
url = "https://192.168.1.20:8443"

[local_policy]
path = "data/policy.toml"
fail_safe = "last_known_valid"

[adapters]
network = "windows-powershell"
firewall = "windows-powershell"
sql = "windows-powershell"
```

### 3.3 Policy Example

```toml
[host]
enabled = true

[internet]
allowed = true

[database]
allowed = true
server = "192.168.1.10"
port = 1433

[[schedule]]
days = ["mon", "tue", "wed", "thu", "fri"]
start = "08:00"
end = "17:00"
timezone = "Asia/Bangkok"

[[ports.allow]]
protocol = "tcp"
remote_port = 1433
remote_address = "192.168.1.10"
purpose = "SQL Server"
```

## 4. Configuration Rules
1. Example config committed to Git
2. Production config may be local/non-secret
3. Secrets stored outside ordinary TOML or referenced indirectly
4. Config validated before service starts
5. Unknown critical keys fail fast
6. Every config load reports source + revision/hash
7. Policy has schema version
8. Config reload behavior documented

## 5. Runtime Components

### 5.1 Central Control Core
Responsibilities:
- host registry
- policy registry/versioning
- authorization
- command dispatch
- state aggregation
- alarm aggregation
- audit
- API
- single-point management contract

### 5.2 Local Agent
Responsibilities:
- Windows background service
- authenticated command reception
- validated policy cache
- schedule evaluation
- reconciliation
- telemetry
- local health
- continue safe operation during temporary Core/UI outage

### 5.3 PowerShell Adapter Modules
Responsibilities:
- Windows-specific read/apply/verify
- structured object/JSON contract
- no business policy
- no UI
- no arbitrary shell capability

## 6. Central Monitoring & Observability

### 6.1 Central Dashboard Minimum View
Dashboard หน้าแรกควรแสดง:
- overall system health
- host count online/stale/offline
- DB Server state
- SQL health
- Internet policy state per host
- DB access state per host
- current schedule/effective permission
- active alarms
- policy drift
- last heartbeat age
- last failed command
- maintenance state
- policy revision

### 6.2 Health States
STARTING, HEALTHY, DEGRADED, UNHEALTHY, STOPPING

### 6.3 Minimum Metrics
Per Agent:
- heartbeat age
- reconciliation duration
- reconciliation success/fail
- policy revision
- policy apply duration
- adapter errors
- drift count
- last successful verification
- command queue depth

Core:
- connected agents
- stale/offline agents
- active alarms by severity
- command success/fail rate
- telemetry age
- API health

### 6.4 Structured Logs
Baseline fields:
- timestamp
- level
- component
- hostId
- operation
- correlationId
- policyRevision
- result
- durationMs
- errorCode

Never log secrets.

### 6.5 Health Endpoints
Core:
- /health/live
- /health/ready
- /status
- /metrics or equivalent

Agent:
- equivalent local status contract

### 6.6 Freshness
UI must display value + source + timestamp + age and clearly mark STALE/OFFLINE.

## 7. Central Control UX Rules
1. One host can be selected for detailed control
2. Multiple hosts can be grouped for approved bulk policy operations
3. Destructive/high-impact actions require confirmation and impact summary
4. Emergency actions require reason
5. Dashboard must not expose raw arbitrary PowerShell execution
6. Technical details are secondary view, not primary operator view
7. Common tasks should be achievable in few steps
8. State colors/icons are supplemental; text state must always exist
9. UI must show whether displayed state is Desired, Actual, or Effective

## 8. Testing Strategy

### 8.1 Unit Tests
- policy resolution
- schedule boundaries
- priority
- state transitions
- alarms
- config validation
- reconciliation planning

### 8.2 Contract Tests
- Python ↔ PowerShell schema
- Core ↔ Agent protocol
- config compatibility
- policy revision

### 8.3 PowerShell Tests
Use Pester:
- validation
- object shape
- mocked cmdlets
- error handling
- idempotency

### 8.4 Integration Tests
Controlled Windows environment:
- read-only Get-Net*
- project-owned firewall rules
- test route operations
- SQL TCP probe

### 8.5 Scenario Tests
- schedule boundary
- manual override
- Core offline
- Agent restart
- firewall drift
- DB unavailable
- policy stale
- adapter timeout
- maintenance enter/exit
- dashboard state stale/offline

### 8.6 Acceptance Tests
Map directly to Requirement IDs and Use Case IDs.

## 9. Test Seams
Core depends on interfaces:
- ClockPort
- NetworkPort
- FirewallPort
- SqlPort
- PolicyStore
- AuditStore
- TransportPort

Production injects Windows implementations.
Tests inject fake/in-memory implementations.

## 10. CI Pipeline

```text
Checkout
  ↓
Validate TOML / schemas
  ↓
Python lint
  ↓
Python type checks
  ↓
Python unit tests
  ↓
Contract tests
  ↓
PowerShell static analysis
  ↓
Pester unit tests
  ↓
Package validation
  ↓
Windows integration tests (protected runner)
  ↓
Acceptance/scenario tests
  ↓
Evidence artifacts
```

Destructive integration tests must never run on ordinary developer workstation or production by default.

## 11. Work Packages

### WP-01 Repository & Tooling
pyproject, package layout, TOML examples, lint/type/test tools, CI

### WP-02 Contracts & Models
result/state/alarm/policy/message/error models

### WP-03 Config System
TOML loader, validation, defaults, revision/hash, tests

### WP-04 Fake Adapters
Build fakes before destructive adapters

### WP-05 Observability Foundation
structured logger, correlation IDs, health, metrics, audit

### WP-06 Read-Only Windows Adapters
Network, Firewall, Services, SQL connectivity

### WP-07 Read-Only Agent
service loop, heartbeat, status, local cache, self-test

### WP-08 Core + Transport
registration, heartbeat ingestion, state registry, policy registry, commands

### WP-09 Central Status Console
minimal operator console to prove single-point monitoring before full dashboard

### WP-10 Policy + Scheduler
schedule, priority, override, FakeClock

### WP-11 Enforcement Adapters
1. project-owned firewall
2. DB access
3. Internet access
4. port policy
5. maintenance route

Each requires plan/apply/verify/rollback.

### WP-12 Reconciliation & Drift
desired vs actual, safe converge, drift alarms

### WP-13 Central Control UI
user-friendly control surface for approved operations

### WP-14 Packaging & Windows Service
installer, service registration, config, upgrade/uninstall/rollback

## 12. Implementation Order
Read → Model → Fake → Observe → Test → Real Adapter → Verify → Automate → Central UI

## 13. Definition of Ready
- requirement/use case known
- contract known
- failure behavior known
- test approach known
- security impact reviewed
- config ownership defined

## 14. Definition of Done
- implementation matches SSOT
- config documented
- central status visible
- structured monitoring available
- automated unit/contract tests pass
- integration evidence where required
- no secrets
- rollback/recovery documented
- traceability updated
