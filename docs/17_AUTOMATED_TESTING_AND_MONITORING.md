# 17 — Automated Testing & Monitoring Strategy

- Status: ACCEPTED
- Purpose: กำหนดวิธีทำให้ MTP6CoopNW ตรวจสอบได้อัตโนมัติและหา fault ได้ง่ายตั้งแต่ development ถึง production

## 1. Testing Pyramid

```text
              Acceptance / Scenario
             -----------------------
             Windows Integration
           -------------------------
          Contract / Adapter Tests
        -----------------------------
        Unit / Pure Logic Tests
```

จำนวน test ควรมากที่สุดที่ Unit และน้อยที่สุดที่ destructive integration.

## 2. Python Tooling Baseline

Recommended responsibilities:
- pytest: unit/contract/scenario
- coverage: coverage reporting
- static type checker: one project-standard tool
- linter/formatter: one project-standard tool

Tool versions shall be pinned/managed in project configuration once implementation begins.

## 3. PowerShell Tooling Baseline

- Pester for tests
- PSScriptAnalyzer for static analysis
- modules imported from controlled project paths
- mocks for Windows cmdlets in ordinary CI

## 4. Test Markers

Suggested categories:
- unit
- contract
- scenario
- windows
- destructive
- acceptance

Rules:
- default test command excludes destructive
- destructive requires explicit flag/environment
- production host must never be automatic test target

## 5. Fake-First Principle

For every new adapter contract:
1. interface
2. fake implementation
3. Core tests
4. PowerShell implementation
5. adapter contract test
6. Windows integration test

This prevents Windows details from defining business semantics.

## 6. Time Testing

Schedules must never depend directly on wall clock in business logic.

Inject ClockPort:
- now()
- timezone()
- monotonic() where needed

Tests cover:
- before start
- exact start
- inside window
- exact end
- after end
- midnight crossover
- weekday transition
- restart
- clock skew detection

## 7. Network/Firewall Testing Safety

Three levels:

### Level 0 — Pure Fake
No Windows changes.

### Level 1 — Mocked PowerShell
Pester mocks native cmdlets.

### Level 2 — Controlled Windows Integration
Dedicated VM/test endpoint, project-owned rules only.

Production-like destructive test requires explicit approval.

## 8. Monitoring as Test Oracle

Verification uses the same observable state used by monitoring.

Example:
- command says Internet BLOCKED
- telemetry reads route/firewall/connectivity
- verifier confirms Actual matches Desired
- dashboard shows same actual state

This prevents UI success messages from being trusted without read-back.

## 9. Health Model

### Core
- LIVE: process running
- READY: dependencies sufficient to serve control requests
- DEGRADED: some agents/services unavailable
- UNHEALTHY: core function unsafe/unavailable

### Agent
- LIVE
- READY
- DEGRADED
- UNHEALTHY
- STALE at central view
- OFFLINE at central view

## 10. Alarm Test Cases

Every alarm rule must have:
- trigger test
- non-trigger test
- clear/recovery test
- severity test
- deduplication test where applicable

## 11. CI Workflow Separation

### ci-fast
Runs on normal changes:
- config/schema
- Python unit/contract
- Pester mocked tests
- static analysis

### ci-scenario
Runs scenario simulation using fake adapters.

### ci-windows
Runs on protected/self-hosted Windows test machine:
- adapter integration
- controlled firewall tests
- service tests
- SQL TCP probe

### ci-release
Runs:
- all required gates
- package
- version consistency
- evidence manifest

## 12. Evidence Automation

CI outputs should include:
- test results
- coverage
- lint/type results
- Pester results
- scenario summary
- package hash/version
- config/schema version

Do not commit bulky runtime artifacts into repository; use CI artifacts where appropriate.

## 13. Production Monitoring Minimum

Central dashboard:
- Core health
- Agent online/stale/offline
- latest heartbeat
- policy revision
- reconcile result
- drift
- alarms
- command failures
- DB reachability
- effective Internet/DB status

## 14. Diagnostics Bundle

A support bundle should be generatable without secrets and contain:
- versions
- sanitized config summary
- host status
- adapter self-test
- recent structured logs
- policy revision
- network/firewall project-owned state
- SQL connectivity result
- timestamps/clock status

## 15. Quality Gate

No feature is accepted if:
- it cannot be tested without UI
- it cannot report health/state
- it has no structured error
- it has no verification/read-back for state change
- it has no automated test at the appropriate layer
