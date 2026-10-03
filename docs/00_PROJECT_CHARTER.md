# 00 — Project Charter

## Project Name
MTP6CoopNW — Network & SQL Control Platform

## Mission
สร้าง control platform ขนาดเล็กที่บริหาร network, SQL connectivity, firewall, maintenance mode, diagnostics, backup visibility และ audit ของระบบสหกรณ์ ภ.6 ได้อย่างปลอดภัย ตรวจสอบย้อนหลังได้ และไม่ผูกกับ UI ใด UI หนึ่ง

## Operating Principles

### 1. Document First
เอกสารกำหนด behavior และ contract ก่อน implementation

### 2. Engine First
Business/control logic อยู่ใน Engine Layer เท่านั้น

### 3. Replaceable UI
PowerShell CLI, WinForms, WPF, Web, REST, Mobile หรือ UI ในอนาคตต้องเป็น shell ที่เรียก Application/Engine contract เดียวกัน

### 4. Safe Change
operation ที่เปลี่ยน network/firewall/system state ต้องเป็น Read → Validate → Plan → Apply → Verify → Commit Result และหาก Verify ไม่ผ่านต้องพยายาม Rollback

### 5. Idempotency
คำสั่งซ้ำต้องไม่ทำให้ state เสีย

### 6. Least Privilege
เปิดสิทธิ์และ port เท่าที่จำเป็น SQL Server ต้องไม่ถูก expose สู่ Internet

### 7. Evidence Always
ผลการเปลี่ยนแปลงและ test ต้องมี structured result/log ที่ตรวจสอบย้อนหลังได้

## Scope v1
- Network configuration/status
- DB Server Normal/Maintenance mode
- Windows Firewall management สำหรับ SQL
- SQL Server service/port/connectivity diagnostics
- Client connectivity checks
- Internet reachability checks
- Configuration management
- Audit logging
- Backup status visibility
- CLI/PowerShell shell แรก

## Out of Scope v1
- การแก้ business data ในฐานข้อมูล
- Cloud orchestration
- Domain/Active Directory management
- Automatic Internet port forwarding
- Direct public exposure ของ SQL Server
- Mobile app implementation

## Success Criteria
- Client 5 เครื่องเข้าถึง DB Server ผ่าน LAN ได้เสถียร
- Client Internet ไม่ได้รับผลจากการสลับ mode ของ DB Server
- DB Server Normal Mode ออก Internet ไม่ได้
- DB Server Maintenance Mode ออก Internet ได้ตามที่กำหนด
- SQL inbound รับเฉพาะ trusted LAN/client sources
- ทุก state transition ตรวจสอบผลได้
- UI เปลี่ยนได้โดยไม่ย้าย business logic
