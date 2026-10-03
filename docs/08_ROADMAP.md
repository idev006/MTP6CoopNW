# 08 — Roadmap

## Phase 0 — Documentation Baseline
Status: STARTED
- Establish SSOT
- Define requirements
- Define architecture
- Define network/security/operations
- Define engine contracts
- Define testing policy

Exit: documents reviewed and baseline assumptions verified onsite

## Phase 1 — Engine Foundation
- Repository source structure
- Config schema + validator
- Common result/error model
- Audit engine
- Diagnostics read-only engine
- Unit tests

Exit: read-only diagnostics stable

## Phase 2 — Network & Firewall Engines
- NetworkEngine desired-state operations
- FirewallEngine project-owned SQL rules
- Rollback strategy
- Integration tests

Exit: safe repeatable configuration on test machines

## Phase 3 — Maintenance Orchestration
- MaintenanceEngine
- Enable/Disable Maintenance
- Verification gates
- Audit/evidence output

Exit: acceptance tests for Normal/Maintenance transitions pass

## Phase 4 — SQL & Backup Visibility
- SqlEngine diagnostics
- SQL connection test
- Backup status/reporting

## Phase 5 — First UI Shell
- Minimal PowerShell CLI/menu
- UI contains no business logic

## Phase 6 — Desktop/Web UI Options
เลือกตามความต้องการโดยไม่แก้ Engine semantics:
- WPF/WinUI desktop
- Local web dashboard
- REST API + remote administration UI

## Deferred
- Central multi-host agent architecture
- Notifications
- Automated backup scheduling/retention
- Mobile client

## Gate Rule
ห้ามข้าม phase เพื่อเร่งสร้าง UI หาก Engine contract และ safety tests ยังไม่ผ่าน
