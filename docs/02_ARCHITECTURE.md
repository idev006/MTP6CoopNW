# 02 — Architecture

## Architectural Style
Engine-first, UI-independent, process-oriented control platform

## Control-Room Concept
MTP6CoopNW ใช้แนวคิดเดียวกับ dashboard ควบคุมสายการผลิตในโรงงาน:
- **Sensors/Telemetry** = network, SQL, firewall, services, disk, backup, internet status
- **State Model** = สถานะกระบวนการของระบบ
- **Control Engine** = logic ที่ตัดสินใจว่าจะอนุญาต operation ใด
- **Interlock** = เงื่อนไขที่ต้องผ่านก่อนเปลี่ยน state
- **Alarm/Warning** = deviation จาก desired state
- **Operator Action** = คำสั่งจาก UI
- **Recovery Sequence** = workflow กลับสู่ safe state
- **Historian/Audit** = log/evidence ย้อนหลัง

## Layer Model

UI Layer → Application/Control Layer → Process/State Layer → Engine Layer → Windows/Infrastructure

### UI Layer
PowerShell Menu, CLI, WinForms, WPF, Web, REST client หรือ platform อื่น

ข้อกำหนด: UI ทำหน้าที่รับ input และแสดงผลเท่านั้น ห้ามมี business/control logic สำคัญ

### Application / Control Layer
Use-case orchestration เช่น ConfigureServer, ConfigureClient, EnableMaintenanceMode, DisableMaintenanceMode, RunDiagnostics, RecoverFault

### Process / State Layer
ทำหน้าที่:
- classify current state
- evaluate interlocks
- determine allowed transitions
- aggregate alarms/warnings
- expose next safe action
- coordinate recovery sequence

### Engine Layer
- NetworkEngine
- FirewallEngine
- SqlEngine
- MaintenanceEngine
- DiagnosticsEngine
- BackupEngine
- AlarmEngine
- StateEngine
- AuditEngine

### Infrastructure Layer
Windows Networking, Windows Firewall, PowerShell/CIM, SQL Server, Services, Event Log และ file system

## State Model
สถานะขั้นต่ำ:
- SERVER_NORMAL
- SERVER_MAINTENANCE
- CLIENT
- WARNING
- FAULT
- RECOVERY
- UNKNOWN
- ERROR

## Example State Transition
SERVER_NORMAL
→ precheck/interlock
→ SERVER_MAINTENANCE
→ maintenance task
→ verification
→ SERVER_NORMAL

Fault path:
ANY STATE
→ FAULT
→ DIAGNOSE
→ RECOVERY
→ VERIFY
→ target safe state

## Transition Rule
ทุก state-changing operation ต้องทำตามลำดับ:
1. Read current state
2. Validate prerequisites
3. Evaluate interlocks
4. Build change plan
5. Apply
6. Verify target state
7. Re-evaluate alarms
8. Record audit result
9. Rollback เมื่อ verification ล้มเหลวและ rollback ปลอดภัย

## Dashboard Information Model
Dashboard ควรแสดงอย่างน้อย:
- Overall system state
- DB Server state
- Client 1–5 state
- SQL service/connectivity
- Network/LAN health
- Internet state
- Firewall/security state
- Backup health
- Active alarms/warnings
- Maintenance state
- Last operation/result
- Recommended/allowed next actions

## Design Constraints
- Engine ต้องไม่เขียน UI output โดยตรง
- Engine คืน structured object/result
- Config ต้อง externalized
- Secrets ห้ามอยู่ใน source code
- Operation ต้อง idempotent เท่าที่ทำได้
- Network changes ต้องป้องกัน self-lockout
- Alarm ต้องแยกระหว่าง information, warning, fault และ critical condition
- UI ต้องไม่ bypass interlock/control policy

## Future Compatibility
Application boundary ควรสามารถครอบด้วย REST API ได้ในอนาคตโดยไม่เปลี่ยน Engine semantics
