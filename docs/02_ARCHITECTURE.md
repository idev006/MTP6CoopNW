# 02 — Architecture

## Architectural Style
Engine-first, UI-independent, process-oriented, policy-driven distributed control platform

## Control-Room Concept
MTP6CoopNW ใช้แนวคิดเดียวกับ dashboard ควบคุมสายการผลิตในโรงงาน:
- Sensors/Telemetry = network, SQL, firewall, services, disk, backup, internet status
- State Model = สถานะกระบวนการของระบบ
- Policy = desired permissions/schedules
- Control Engine = logic ที่ตัดสินใจว่าจะอนุญาต operation ใด
- Interlock = เงื่อนไขที่ต้องผ่านก่อนเปลี่ยน state
- Alarm/Warning = deviation จาก desired state
- Operator Action = คำสั่งจาก UI
- Recovery Sequence = workflow กลับสู่ safe state
- Historian/Audit = log/evidence ย้อนหลัง

## Distributed Control Model

Central Control Plane
→ authenticated command/policy channel
→ Local Agent / Enforcement Engine on each managed host
→ Windows Networking / Firewall / SQL connectivity

Local Agents
→ heartbeat / telemetry / command result
→ Central Control Plane
→ UI/API

### Why Local Agent
การบังคับใช้ schedule, Internet, DB และ port policy ต้องไม่พึ่ง UI และไม่ควรพึ่ง remote PowerShell session ทุกครั้ง

Agent ทำให้:
- schedule ทำงานแม้ UI ปิด
- enforcement อยู่ใกล้ resource ที่ควบคุม
- report actual state ได้ต่อเนื่อง
- detect drift ได้
- reconnect แล้ว reconcile desired/actual state ได้

## Layer Model

UI Layer
→ Application / Control API
→ Policy + Process / State Layer
→ Module/Core Layer
→ Node Agent + Capability Modules
→ Windows / SQL / Network

### UI Layer
PowerShell Menu, CLI, WinForms, WPF, Web, REST client หรือ platform อื่น

UI รับ input และแสดงผลเท่านั้น ห้ามมี business/control logic สำคัญ

### Application / Control Layer
Use-case orchestration เช่น ConfigureHost, SetUsageSchedule, SetInternetAccess, SetDatabaseAccess, SetPortPolicy, EnableMaintenanceMode, RunDiagnostics

### Policy Layer
กำหนด Desired State เช่น:
- host enabled/disabled
- schedule
- internet allow/deny
- database allow/deny
- port allow/deny
- maintenance permission

Policy ต้อง versioned

### Process / State Layer
- classify current state
- evaluate schedule
- evaluate interlocks
- resolve manual override vs schedule
- determine allowed transitions
- aggregate alarms/warnings
- expose next safe action
- coordinate recovery

### Core / Module Layer
Core:
- Command Bus
- Event Bus
- Module Manager
- Policy Registry
- State Registry
- Audit
- Security
- Result Contract

Capability Modules:
- NetworkModule
- FirewallModule
- SqlModule
- AccessControlModule
- SchedulerModule
- MaintenanceModule
- DiagnosticsModule
- BackupModule
- AlarmModule
- TelemetryModule

### Local Agent
Agent ต้องเป็น background service/process ที่:
- โหลด validated last-known policy
- evaluate schedule
- execute approved local commands
- enforce firewall/network rules
- collect telemetry
- emit heartbeat
- return structured command result
- persist minimal safe state required for restart

### Infrastructure Layer
Windows Networking, Windows Firewall, PowerShell/CIM, SQL Server, Services, Event Log และ file system

## Host Effective Policy Model
แต่ละเครื่องควรมี effective policy ในเชิงแนวคิด:

HostPolicy
- hostEnabled
- schedule
- internetAccess
- databaseAccess
- portPolicies[]
- maintenancePolicy
- revision
- effectiveFrom

Actual State ต้องถูกเปรียบเทียบกับ Desired State เสมอ

## State Model
สถานะขั้นต่ำ:
- NORMAL
- DISABLED
- SCHEDULE_BLOCKED
- MAINTENANCE
- WARNING
- FAULT
- RECOVERY
- UNKNOWN
- OFFLINE

## Policy Priority
ลำดับ priority ต้อง explicit และ configurable โดย baseline:
1. Safety/Critical policy
2. Administrative emergency disable
3. Approved manual override
4. Maintenance policy
5. Schedule policy
6. Default host policy

ห้ามใช้ implicit priority ใน code

## Real-Time / Near-Real-Time Communication

Baseline:
- Agent heartbeat: configurable, target 2–5 seconds on LAN
- Command acknowledgement: immediate when connected
- State change event: push when possible
- Periodic reconciliation: required even when push exists

Transport implementation สามารถเปลี่ยนได้โดย contract ต้องคงเดิม เช่น:
- WebSocket
- authenticated local REST + polling
- named pipe for local UI
- future message broker

UI ไม่ควรคุยกับ Agent โดยตรงข้าม policy/control layer ยกเว้น diagnostic path ที่กำหนดไว้

## Example State Transition

Scheduled access:
ALLOWED
→ schedule boundary reached
→ evaluate interlock/policy
→ BLOCKED
→ enforce internet/db/port rules
→ verify
→ publish state
→ audit

Manual override:
BLOCKED
→ authorized override
→ policy resolution
→ enforce
→ verify
→ publish
→ audit

Fault:
ANY STATE
→ FAULT
→ DIAGNOSE
→ RECOVERY
→ VERIFY
→ target safe state

## Dashboard Information Model
Dashboard ควรแสดงอย่างน้อย:
- Overall system state
- Host 1..N online/offline
- Current host permission
- Schedule/effective time window
- Internet permission + actual state
- DB permission + actual reachability
- Managed port state
- DB Server / SQL service
- Network/LAN health
- Firewall/security state
- Backup health
- Active alarms/warnings
- Last heartbeat
- Policy revision
- Last command/result
- Recommended/allowed next actions

## Design Constraints
- Engine ต้องไม่เขียน UI output โดยตรง
- Engine คืน structured object/result
- Config/Policy ต้อง externalized
- Secrets ห้ามอยู่ใน source code
- Operation ต้อง idempotent เท่าที่ทำได้
- Network changes ต้องป้องกัน self-lockout
- Alarm ต้องแยกระหว่าง information, warning, fault และ critical condition
- UI ต้องไม่ bypass interlock/control policy
- Agent ต้องไม่สูญเสีย last-known policy เพียงเพราะ UI/Core ชั่วคราว unavailable
- Port rules ต้องเป็น project-owned rules และตรวจ ownership ก่อนแก้/ลบ

## Future Compatibility
Transport, UI และ platform adapter สามารถเปลี่ยนได้โดยไม่เปลี่ยน policy semantics หรือ module contracts


## State / Stage / Cycle Model

MTP6CoopNW แยกสามแนวคิดอย่างชัดเจน:

### State
สถานะคงอยู่ของ host/subsystem เช่น NORMAL, DISABLED, MAINTENANCE, FAULT

### Stage
ขั้นของ operation ปัจจุบัน เช่น REQUESTED → VALIDATING → PLANNING → APPLYING → VERIFYING → COMPLETED

Failure path:
FAILED → ROLLING_BACK → ROLLED_BACK หรือ ROLLBACK_FAILED

Additional terminal stages:
- CANCELLED
- TIMED_OUT

### Cycle
วงรอบควบคุมที่ทำซ้ำ:
Read Policy → Read Actual → Evaluate Schedule → Resolve Effective Policy → Compare → Interlock → Reconcile → Verify → Publish → Audit/Alarm → Wait

### Fast / Slow Cycle
Fast cycle ใช้กับ heartbeat, command result, critical state และ policy revision
Slow cycle ใช้กับ drift, SQL/service health, disk, backup และ diagnostics เชิงลึก

ทุก interval ต้อง configurable และ testable ผ่าน ClockPort/FakeClock.

### Stage Timeout
ทุก stage ที่รอ external effect ต้องมี timeout ที่กำหนดได้ และ timeout ต้องแปลงเป็น explicit stage/error ไม่ถือเป็น success.
