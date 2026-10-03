# 01 — System Requirements

## Functional Requirements

### FR-001 — Database Server
รองรับ Windows Database Server 1 เครื่อง รัน Microsoft SQL Server และมี NIC 1 ใบ

### FR-002 — Clients
รองรับ Windows Client อย่างน้อย 5 เครื่อง เชื่อมฐานข้อมูลเดียวกันผ่าน LAN

### FR-003 — Client Internet
Client ต้องใช้งาน Internet ได้ตาม policy รายเครื่อง และไม่ขึ้นกับ Maintenance Mode ของ Database Server

### FR-004 — Server Normal Mode
- DB Server คง LAN connectivity
- Client ที่ได้รับอนุญาตเข้าถึง SQL ได้
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
IP/port/allowed clients ต้องอยู่ใน config/policy ไม่ hard-code ใน Engine

### FR-011 — Per-Host Usage Schedule
แต่ละเครื่องต้องสามารถกำหนดวันและช่วงเวลาที่อนุญาตให้ใช้งานได้เป็นรายเครื่อง

Policy ต้องรองรับอย่างน้อย:
- days of week
- start time / end time
- enabled/disabled
- timezone
- optional exception/override

การบังคับใช้ schedule ต้องเกิดใน Engine/Agent ไม่ขึ้นกับการเปิด UI

### FR-012 — Per-Host Administrative Enable/Disable
ผู้ดูแลต้องสามารถสั่ง Enable/Disable การอนุญาตใช้งานของแต่ละเครื่องได้ โดย manual override ต้องมี priority ชัดเจนเหนือ/ใต้ schedule ตาม policy ที่กำหนด และต้อง audit ทุกครั้ง

### FR-013 — Per-Host Internet Access Control
ผู้ดูแลและ policy engine ต้องสามารถ Allow/Deny Internet egress เป็นรายเครื่อง โดยต้องรักษา LAN/control-plane connectivity ที่จำเป็น

### FR-014 — Per-Host Database Access Control
ผู้ดูแลและ policy engine ต้องสามารถ Allow/Deny การเข้าถึง Database Server เป็นราย Client ได้ โดยไม่จำเป็นต้องหยุด SQL Server ทั้งระบบ

### FR-015 — Port Access Policy
ระบบต้องกำหนด Allow/Deny port policy ได้อย่างน้อยตาม:
- target host
- direction
- protocol TCP/UDP
- local/remote port
- remote address/host group
- enabled/disabled state

FirewallEngine ต้องเป็นผู้บังคับใช้ policy และต้องสามารถตรวจ drift จาก desired state

### FR-016 — Real-Time / Near-Real-Time Status
Engine/Agent และ UI ต้องสามารถสื่อสารสถานะระบบแบบ real-time หรือ near-real-time

สถานะขั้นต่ำ:
- host online/offline
- last heartbeat
- current usage permission
- schedule state
- Internet allowed/blocked
- DB allowed/blocked
- managed port/firewall state
- SQL reachability
- active alarms
- last command/result

### FR-017 — Local Enforcement Agent
แต่ละเครื่องที่อยู่ภายใต้การควบคุมต้องมี local agent/engine หรือ equivalent enforcement component ที่:
- รับ policy/command
- บังคับใช้ policy บนเครื่องตนเอง
- ทำงานได้แม้ UI ไม่เปิด
- รายงาน heartbeat/status
- เก็บ last-known policy อย่างปลอดภัย
- ไม่ bypass security/interlock ของ Core

### FR-018 — Central Control Plane
ต้องมี Control Core ที่เป็นแหล่ง authoritative สำหรับ desired policy/state และทำหน้าที่:
- policy distribution
- command orchestration
- state aggregation
- alarm aggregation
- audit
- UI/API contract

## Minimum Use Cases

### UC-001 — Set Allowed Usage Schedule
ผู้ดูแลเลือก Client แล้วกำหนดวัน/เวลาใช้งาน ระบบ validate policy, distribute ไป Agent และแสดง effective schedule

### UC-002 — Force Enable/Disable Host Usage
ผู้ดูแล override การอนุญาตใช้งานเครื่องทันที พร้อมเหตุผลและ audit

### UC-003 — Allow/Block Internet
ผู้ดูแลหรือ schedule สั่ง Internet Allow/Deny เป็นรายเครื่อง โดย LAN control channel ต้องคงอยู่ตาม design

### UC-004 — Allow/Block Database Access
ผู้ดูแลหรือ policy สั่ง DB Allow/Deny ราย Client และตรวจผลจริงด้วย connectivity check

### UC-005 — Manage Ports
ผู้ดูแลเพิ่ม/แก้/ปิด port policy แล้ว Agent converge Windows Firewall ไป desired state

### UC-006 — Live Dashboard
Dashboard แสดงสถานะทุก host และ subsystem แบบ near-real-time พร้อม alarm และ last update

### UC-007 — Policy Drift Detection
หาก Windows Firewall/route ถูกแก้ด้วยมือจนไม่ตรง policy ระบบต้องตรวจพบและรายงาน drift และสามารถ reconcile ตามสิทธิ์/policy

### UC-008 — Scheduled Automatic Transition
เมื่อถึงเวลา Agent ต้องเปลี่ยน effective permission ตาม schedule โดยไม่ต้องมี UI เปิดอยู่ และบันทึกผล

## Non-Functional Requirements

- NFR-001 Safety: network/firewall change ต้องมี pre-check และ post-check
- NFR-002 Idempotency: operation สำคัญต้องเรียกซ้ำได้อย่างปลอดภัย
- NFR-003 UI Independence: Engine ห้ามพึ่ง WinForms/WPF/Web/Console
- NFR-004 Privilege: ตรวจ Administrator/service privilege ก่อน operation ที่ต้องใช้สิทธิ์สูง
- NFR-005 Observability: error ต้องมี code/message และ log ได้
- NFR-006 Recoverability: network/firewall operation ต้องมี rollback strategy
- NFR-007 Near-Real-Time Target: heartbeat/status interval ต้อง configurable; baseline design target 2–5 วินาทีบน LAN โดยไม่ถือเป็น hard real-time guarantee
- NFR-008 Offline Tolerance: Agent ต้อง enforce last-known valid policy ได้เมื่อ Control Core/UI ติดต่อไม่ได้ตาม fail-safe policy
- NFR-009 Clock/Timezone: schedule evaluation ต้องใช้ timezone ที่กำหนดและจัดการ clock skew อย่างตรวจสอบได้
- NFR-010 Secure Control Channel: command/policy/status channel ต้อง authenticate endpoints และป้องกัน unauthorized command
- NFR-011 Policy Versioning: policy ทุกชุดต้องมี version/revision เพื่อ audit และ reconcile
- NFR-012 Fail-Safe: loss of dashboard connection ต้องไม่ทำให้ firewall/access policy ถูกยกเลิกโดยอัตโนมัติ

## Baseline Inventory
- 16-port Ethernet switch 1 ตัว
- LAN cable สำหรับ 6 hosts จำนวน 6 เส้น
- ต้องมี uplink switch-router เพิ่มอีก 1 เส้น หากยังไม่มี
- DB Server 1 เครื่อง
- Client 5 เครื่อง
- NIC 1 ใบต่อเครื่อง
