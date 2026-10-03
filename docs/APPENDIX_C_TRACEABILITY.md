# Appendix C — Traceability Matrix

## Purpose
ใช้เชื่อมโยง requirement ตั้งแต่เอกสารจนถึง implementation และหลักฐาน เพื่อให้ตรวจสอบได้ว่าแต่ละความสามารถถูกออกแบบ พัฒนา และทดสอบครบหรือไม่

## Baseline Matrix

| Requirement | Use Case | Primary Engine/Module | Adapter | Test/Evidence |
|---|---|---|---|---|
| FR-011 Per-Host Schedule | UC-002, UC-007 | PolicyEngine, SchedulerEngine | Time Adapter, Persistence Adapter | schedule unit/integration/acceptance |
| FR-012 Host Enable/Disable | UC-003, UC-016 | AccessControlEngine, PolicyEngine | Firewall/Enforcement Adapter | enable-disable acceptance |
| FR-013 Internet Control | UC-004 | PolicyEngine, Network/Firewall Module | Windows Network + Firewall | LAN preserved, Internet allow/deny |
| FR-014 DB Access Control | UC-005 | PolicyEngine, FirewallEngine, SqlEngine | Firewall + SQL Connectivity | DB allow/deny verification |
| FR-015 Port Policy | UC-006, UC-018 | FirewallEngine | Windows Firewall Adapter | managed rule/read-back test |
| FR-016 Near-Real-Time Status | UC-008, UC-013 | TelemetryEngine, StateEngine | Transport Adapter | heartbeat latency/stale detection |
| FR-017 Local Agent | UC-001, UC-014, UC-017 | AgentEngine | Persistence/Transport | restart/offline/reconnect |
| FR-018 Central Control Plane | UC-001..020 | Control Core | Transport/Audit | integration/system acceptance |

## Rules
1. Feature ห้ามถือว่า complete หากไม่มี requirement/use case link
2. Adapter ใหม่ต้องมี integration test
3. State-changing use case ต้องมี acceptance test
4. Security-critical requirement ต้องมี negative test
5. Matrix ต้องขยายเมื่อ implementation/test IDs ถูกกำหนดจริง
