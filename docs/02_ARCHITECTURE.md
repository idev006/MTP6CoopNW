# 02 — Architecture

## Architectural Style
Engine-first, UI-independent control platform

## Layer Model

UI Layer → Application/Control Layer → Engine Layer → Windows/Infrastructure

### UI Layer
PowerShell Menu, CLI, WinForms, WPF, Web, REST client หรือ platform อื่น

ข้อกำหนด: UI ทำหน้าที่รับ input และแสดงผลเท่านั้น ห้ามมี business/control logic สำคัญ

### Application / Control Layer
Use-case orchestration เช่น ConfigureServer, ConfigureClient, EnableMaintenanceMode, DisableMaintenanceMode, RunDiagnostics

### Engine Layer
- NetworkEngine
- FirewallEngine
- SqlEngine
- MaintenanceEngine
- DiagnosticsEngine
- BackupEngine
- AuditEngine

### Infrastructure Layer
Windows Networking, Windows Firewall, PowerShell/CIM, SQL Server, Services, Event Log และ file system

## State Model
สถานะขั้นต่ำ:
- SERVER_NORMAL
- SERVER_MAINTENANCE
- CLIENT
- UNKNOWN
- ERROR

## Transition Rule
ทุก state-changing operation ต้องทำตามลำดับ:
1. Read current state
2. Validate prerequisites
3. Build change plan
4. Apply
5. Verify target state
6. Record audit result
7. Rollback เมื่อ verification ล้มเหลวและ rollback ปลอดภัย

## Design Constraints
- Engine ต้องไม่เขียน UI output โดยตรง
- Engine คืน structured object/result
- Config ต้อง externalized
- Secrets ห้ามอยู่ใน source code
- Operation ต้อง idempotent เท่าที่ทำได้
- Network changes ต้องป้องกัน self-lockout

## Future Compatibility
Application boundary ควรสามารถครอบด้วย REST API ได้ในอนาคตโดยไม่เปลี่ยน Engine semantics
