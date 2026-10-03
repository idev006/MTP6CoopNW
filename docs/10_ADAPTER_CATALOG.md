# 10 — Adapter Catalog

## 1. Adapter Principle
Adapter แปลงคำสั่งจาก Core/Module Contract ไปสู่ platform-specific mechanism ห้ามเป็นเจ้าของ business policy หรือ process decision

> Core decides **what**. Process decides **when**. Adapter implements **how**.

## 2. Baseline Technology Decision
- Control Core / Agent logic: Python
- Windows low-level enforcement: PowerShell / CIM / native Windows tooling
- UI: replaceable
- Transport: replaceable behind contract

## 3. Required Adapters

### ADP-001 — Windows Network Adapter
Purpose:
- Read NIC state
- Read/set approved IP parameters
- Read/add/remove managed routes
- Read gateway/DNS/profile
- Verify LAN/router reachability

Possible implementation:
- PowerShell NetTCPIP cmdlets
- CIM where appropriate

Must not:
- Disable NIC merely to block Internet
- Change unmanaged routes without ownership/validation

### ADP-002 — Windows Firewall Adapter
Purpose:
- Create/read/update/remove project-owned firewall rules
- Internet Allow/Deny
- Database Allow/Deny
- Port policy enforcement
- Drift detection

Naming baseline:
- managed rules prefixed with `MTP6CoopNW-`

Must not:
- delete unrelated firewall rules
- expose SQL to WAN

### ADP-003 — Windows Service Adapter
Purpose:
- Inspect/start/stop approved project-related or SQL services when a use case explicitly authorizes it
- Read service health

Must not:
- arbitrarily manipulate unrelated services

### ADP-004 — SQL Connectivity Adapter
Purpose:
- Probe TCP port
- Verify SQL service/reachability
- Optional authenticated connection health check
- Read non-business operational metadata where approved

Must not:
- modify cooperative business data
- embed sa credentials

### ADP-005 — Local Persistence Adapter
Purpose:
- Store last-known validated policy
- Store agent identity/config
- Store minimal local audit queue while Core unavailable

Requirements:
- atomic write
- schema/version validation
- no plaintext secrets unless specifically approved and protected

### ADP-006 — Time Adapter
Purpose:
- Provide normalized local/UTC time
- Timezone evaluation
- Clock-skew detection
- Schedule boundary calculation

### ADP-007 — Transport Adapter
Purpose:
- Core ↔ Agent command/policy/status channel
- authentication
- heartbeat
- state event
- command acknowledgement/result

Candidate mechanisms:
- WebSocket
- HTTPS REST + polling
- future message broker

Transport semantics must remain stable when implementation changes

### ADP-008 — Audit/Log Adapter
Purpose:
- Structured logs
- Local queue
- Central append-oriented audit
- correlationId support

### ADP-009 — Windows Update Adapter (future/optional)
Purpose:
- Detect update readiness/status
- Integrate with approved maintenance workflow

### ADP-010 — Remote Support Adapter (optional)
Purpose:
- Report remote support readiness/status
- Integrate approved remote tool such as AnyDesk
- Must not make remote tool part of Core

### ADP-011 — Notification Adapter (future)
Purpose:
- Emit alarm notifications to approved channels
- UI/transport independent

## 4. Adapter Contract Rules
Every adapter should support:
- `get_capabilities()`
- `self_test()`
- structured input
- structured output
- deterministic error categories
- timeout
- cancellation where practical
- no UI rendering
- no hidden policy decisions

## 5. PowerShell Contract
PowerShell adapters should:
- be module-oriented (`.psm1`) rather than scattered scripts
- accept explicit parameters or JSON
- return objects/JSON, not presentation text
- use terminating errors for controlled failure handling
- avoid global state
- be idempotent/convergent where possible

## 6. Adapter Replacement Rule
A new adapter may replace an existing adapter only if:
- capability contract remains compatible or versioned
- integration tests pass
- security impact reviewed
- ADR created if platform boundary changes
