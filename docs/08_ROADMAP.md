# 08 — Roadmap

## Purpose
บทนี้กำหนดลำดับการพัฒนาและ gate ของโครงการ โดยทุก phase ต้องอ้างอิง Project Book และ SSOT

## Phase 0 — Project Book & Documentation Baseline
Status: IN PROGRESS

Deliverables:
- Project Book structure
- Goals/Objectives/Scope
- Requirements
- Architecture
- Network/Security
- Engine/Adapter contracts
- Use Case catalog
- Workflows/Sequence/State diagrams
- Team/RACI
- Scope & Change Control
- Glossary
- Traceability Matrix
- ADR baseline

Exit:
- chapters internally consistent
- architecture decisions recorded
- baseline assumptions verified onsite
- unresolved questions explicitly recorded

## Phase 1 — Contracts & Repository Foundation
- Python project structure
- PowerShell adapter modules
- schemas
- host identity
- policy revision
- common result/error/event contract
- test foundation

Exit:
- schema validation passes
- no destructive Windows mutation yet

## Phase 2 — Read-Only Agent & Telemetry
- Local Python Agent
- host registration
- heartbeat
- network/firewall/SQL read-only adapters
- state aggregation
- OFFLINE/STALE detection
- status UI/CLI shell

Exit:
- DB Server + Clients visible centrally
- heartbeat/status stable

## Phase 3 — Policy & Scheduler
- Policy Engine
- schedule rules
- priority resolution
- manual override
- local policy persistence
- timezone/clock check
- policy distribution/version reconciliation

Exit:
- schedule simulation/evaluation passes
- restart preserves validated policy

## Phase 4 — Firewall & Access Enforcement
- Internet Allow/Deny
- Database Allow/Deny
- Port Policy
- project-owned firewall rules
- drift detection
- reconciliation
- rollback/recovery

Exit:
- repeatable enforcement
- control channel preserved
- integration tests pass

## Phase 5 — Host Usage & Process Control
- host Enable/Disable
- scheduled transition
- interlocks
- alarms
- recovery
- emergency disable semantics

Exit:
- Must-Have use cases pass

## Phase 6 — DB Server Maintenance
- Normal/Maintenance
- temporary Internet enablement
- Windows Update workflow
- remote support integration
- SQL/LAN preservation verification

## Phase 7 — Operational Dashboard
- selected Desktop/Web UI
- live host tiles
- alarms
- policy/schedule editor
- command results
- audit/history

Rule:
UI contains no Windows enforcement logic

## Phase 8 — Production Hardening
- security review
- installer/package
- agent service recovery
- config migration
- heartbeat/performance tuning
- failure injection
- runbooks
- site acceptance

## Phase 9 — Controlled Rollout
- pilot
- staged Client rollout
- DB Server rollout
- evidence
- post-rollout review

## Future / Optional
- UPS monitoring
- notifications
- alternate remote support adapter
- managed router/firewall API
- message broker
- HA
- richer backup automation
- mobile UI

## Gate Rule
ห้ามข้าม phase เพื่อเร่ง UI หรือ destructive control หาก contract, test, safety และ recovery ของ phase ก่อนหน้ายังไม่ผ่าน
