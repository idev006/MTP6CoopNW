# 09 — Project Definition & Scope Baseline

## 1. Purpose
เอกสารนี้เป็น Project Definition Baseline สำหรับ MTP6CoopNW ใช้ร่วมกันโดยทีม Software, Network, Process, Operations และผู้เกี่ยวข้อง เพื่อให้เข้าใจตรงกันว่าโครงการสร้างอะไร ทำเพื่ออะไร อะไรอยู่ในขอบเขต และอะไรอยู่นอกขอบเขต

## 2. Project Goal
สร้างระบบควบคุมและกำกับการใช้งานเครือข่ายและ Database Server แบบรวมศูนย์ โดยใช้แนวคิด Industrial Control Dashboard มี Central Control Core และ Local Agent รายเครื่อง สามารถบังคับใช้นโยบายตามเวลา ควบคุม Internet/Database/Port แบบรายเครื่อง ตรวจสถานะแบบ near-real-time และบันทึกหลักฐานการเปลี่ยนแปลงได้

## 3. Objectives

### OBJ-001 — Centralized Visibility
ผู้ดูแลเห็นสถานะ Client, DB Server, Agent, SQL, Internet, Firewall, Schedule, Policy และ Alarm จากจุดเดียว

### OBJ-002 — Per-Host Policy Control
กำหนดนโยบายเป็นรายเครื่องได้ ได้แก่:
- วัน/เวลาที่อนุญาตใช้งาน
- Enable/Disable
- Internet Allow/Deny
- Database Allow/Deny
- Port Allow/Deny

### OBJ-003 — Safe Enforcement
ทุก state-changing action ต้องผ่าน Validate → Interlock → Plan → Apply → Verify → Audit และ Rollback เมื่อเหมาะสม

### OBJ-004 — Near-Real-Time Operations
Agent ส่ง heartbeat/status/event กลับส่วนกลาง โดย baseline target 2–5 วินาทีบน LAN

### OBJ-005 — UI Independence
Core/Engine/Agent ต้องไม่ผูกกับ UI เพื่อรองรับ CLI, Desktop, Web, API หรือ UI อื่นในอนาคต

### OBJ-006 — Modular Extensibility
ความสามารถใหม่ต้องเพิ่มผ่าน Module/Adapter/Plugin Contract โดยไม่แก้ Core มากเกินจำเป็น

### OBJ-007 — Policy-Driven Change
การเปลี่ยนนโยบายทั่วไปควรแก้ที่ Policy/Config ก่อนแก้ code

### OBJ-008 — Operational Traceability
ทุก policy revision, operator command, state transition, alarm และผลการตรวจต้องตรวจสอบย้อนหลังได้

### OBJ-009 — Security by Design
SQL Server ต้องไม่เปิดตรงสู่ Internet, secrets ไม่อยู่ใน repo/log, control channel ต้อง authenticate

### OBJ-010 — Maintainability
โค้ด Windows-specific อยู่ใน Adapter Layer และ business/process logic อยู่ใน Python Core

## 4. In Scope

### Control Plane
- Policy management
- Host registry
- State aggregation
- Command orchestration
- Schedule management
- Alarm management
- Audit/event history
- Near-real-time telemetry

### Local Agent
- Background execution
- Last-known-policy persistence
- Schedule evaluation
- Local enforcement
- Heartbeat
- Drift detection
- Self-test
- Reconciliation

### Windows Enforcement
- IP/gateway/route inspection
- Windows Firewall project-owned rules
- Internet access policy
- DB access policy
- Port policy
- Windows service inspection
- SQL connectivity checks

### Operations
- Normal/Maintenance workflows
- Manual override
- Scheduled transitions
- Diagnostics
- Recovery workflow
- Basic backup visibility

## 5. Out of Scope Unless Approved by New ADR/Requirement
- Editing cooperative business data
- Replacing SQL Server application business logic
- WAN exposure of SQL Server
- Automatic router port forwarding
- Full Active Directory administration
- General endpoint management unrelated to project policy
- Antivirus/EDR replacement
- Cloud migration
- Hard real-time guarantees
- PLC/SCADA industrial protocol implementation
- Remote desktop product development
- Destructive backup retention automation in initial releases

## 6. Project Constraints
- Windows endpoints
- 1 NIC per host baseline
- 1 DB Server + at least 5 Clients
- Existing 16-port switch
- LAN-first deployment
- DB Server Internet access restricted by policy
- PowerShell is Windows enforcement adapter, not business logic owner
- Python is primary control/process implementation baseline

## 7. Success Measures
- 100% managed hosts report effective policy and last heartbeat
- Scheduled transition executes without UI being open
- Manual Internet/DB enable-disable is verifiable
- Firewall/port drift is detectable
- DB Server remains LAN-reachable when Internet is disabled
- UI can be replaced without rewriting enforcement logic
- Critical policy changes produce audit records and verification evidence

## 8. Scope Change Rule
Any request that changes trust boundary, deployment model, agent model, policy priority, control transport, security model or ownership of business logic requires:
1. Requirement update
2. Impact analysis
3. ADR when architectural
4. Test update
5. Evidence before production
