# 01 — System Requirements

## Functional Requirements

### FR-001 — Database Server
รองรับ Windows Database Server 1 เครื่อง รัน Microsoft SQL Server และมี NIC 1 ใบ

### FR-002 — Clients
รองรับ Windows Client อย่างน้อย 5 เครื่อง เชื่อมฐานข้อมูลเดียวกันผ่าน LAN

### FR-003 — Client Internet
Client ต้องใช้งาน Internet ได้โดยไม่ขึ้นกับ Maintenance Mode ของ Database Server

### FR-004 — Server Normal Mode
- DB Server คง LAN connectivity
- Client เข้าถึง SQL ได้
- DB Server ไม่มี Internet egress ตาม baseline policy
- AnyDesk/remote Internet service ไม่ต้องใช้งานได้

### FR-005 — Server Maintenance Mode
- DB Server คง IP LAN เดิม
- SQL/LAN connectivity ต้องไม่ขาด
- DB Server ออก Internet ได้
- รองรับ Windows Update และ AnyDesk ตาม policy

### FR-006 — SQL Firewall
สร้างและตรวจ firewall rule สำหรับ SQL TCP โดยจำกัด trusted source

### FR-007 — Diagnostics
ตรวจ NIC, IP/subnet, gateway, LAN reachability, SQL TCP port, SQL service, Internet reachability และ DNS

### FR-008 — State Reporting
Engine ต้องคืน structured result ที่ UI ทุกชนิดนำไปแสดงผลได้

### FR-009 — Audit
ทุก operation ที่เปลี่ยน state ต้องบันทึก timestamp, operation, before, after, checks และ result

### FR-010 — Configuration
IP/port/allowed clients ต้องอยู่ใน config ไม่ hard-code ใน Engine

## Non-Functional Requirements

- NFR-001 Safety: network/firewall change ต้องมี pre-check และ post-check
- NFR-002 Idempotency: operation สำคัญต้องเรียกซ้ำได้อย่างปลอดภัย
- NFR-003 UI Independence: Engine ห้ามพึ่ง WinForms/WPF/Web/Console
- NFR-004 Privilege: ตรวจ Administrator ก่อน operation ที่ต้องใช้สิทธิ์สูง
- NFR-005 Observability: error ต้องมี code/message และ log ได้
- NFR-006 Recoverability: network/firewall operation ต้องมี rollback strategy

## Baseline Inventory
- 16-port Ethernet switch 1 ตัว
- LAN cable สำหรับ 6 hosts จำนวน 6 เส้น
- ต้องมี uplink switch-router เพิ่มอีก 1 เส้น หากยังไม่มี
- DB Server 1 เครื่อง
- Client 5 เครื่อง
- NIC 1 ใบต่อเครื่อง
