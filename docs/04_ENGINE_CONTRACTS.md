# 04 — Engine Contracts

## Contract Philosophy
Engine เป็น authoritative control logic ของระบบ UI ทุกชนิดต้องเรียกผ่าน Application/Engine contract เดียวกัน

## Common Result Contract
ทุก command ควรคืนข้อมูลเชิงโครงสร้างอย่างน้อย:
- success: boolean
- operation: string
- target: string
- stateBefore
- stateAfter
- checks[]
- warnings[]
- errors[]
- timestamp
- correlationId

Engine ห้ามพึ่งสี console, message box หรือ UI-specific object

## NetworkEngine
Responsibilities:
- Read adapter/IP/subnet/gateway/DNS state
- Validate target adapter
- Build route/gateway change plan
- Apply approved network changes
- Verify LAN state
- Restore prior state when rollback is required

Suggested operations:
- GetNetworkState()
- ValidateNetworkConfig(config)
- SetServerNormalNetwork()
- SetServerMaintenanceNetwork()
- ConfigureClient(clientId)

## FirewallEngine
Responsibilities:
- Inspect managed firewall rules
- Create/update/remove only project-owned rules
- Restrict SQL inbound sources
- Verify effective rule state

Suggested operations:
- GetFirewallState()
- EnsureSqlInboundRule()
- VerifySqlExposure()

Rule ownership: project-created rulesต้องมี stable naming/prefix เช่น MTP6CoopNW-

## SqlEngine
Responsibilities:
- Discover SQL-related Windows services
- Check service state
- Check configured/listening TCP port where possible
- Test TCP/SQL connectivity without modifying business data

Suggested operations:
- GetSqlState()
- TestSqlPort()
- TestDatabaseConnection()

## MaintenanceEngine
Responsibilities:
Orchestrate state transitions โดยใช้ NetworkEngine, FirewallEngine, DiagnosticsEngine และ AuditEngine

Suggested operations:
- GetMode()
- EnableMaintenanceMode()
- DisableMaintenanceMode()

MaintenanceEngine ต้องไม่ duplicate low-level network implementation

## DiagnosticsEngine
Responsibilities:
- Run non-destructive checks
- LAN reachability
- Router reachability
- SQL port reachability
- DNS resolution
- Internet reachability
- Disk/service/basic health checks

## BackupEngine
v1 เน้น visibility/verification ก่อน automation:
- Detect latest known backup
- Report age/status
- Validate configured backup path

ห้ามลบ backup อัตโนมัติใน v1

## AuditEngine
Responsibilities:
- Write append-oriented operation records
- Include before/after/checks/result
- Avoid secrets/passwords/tokens in logs

## Idempotency Rules
- EnableMaintenance เมื่ออยู่ Maintenance แล้วต้อง return success/no-change หรือ equivalent
- DisableMaintenance เมื่ออยู่ Normal แล้วต้อง return success/no-change
- EnsureFirewallRule ต้อง converge ไป desired state ไม่สร้าง rule ซ้ำ
- ConfigureClient ต้องตรวจ current state ก่อนเปลี่ยน

## Error Categories
อย่างน้อยควรแยก:
- VALIDATION_ERROR
- PRIVILEGE_REQUIRED
- CONFIG_ERROR
- NETWORK_APPLY_FAILED
- NETWORK_VERIFY_FAILED
- FIREWALL_FAILED
- SQL_UNREACHABLE
- ROLLBACK_FAILED
- UNKNOWN_ERROR
