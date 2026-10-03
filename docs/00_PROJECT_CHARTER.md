# 00 — Project Charter

## Project Name
MTP6CoopNW — Network & SQL Control Platform

## Mission
สร้าง control platform ขนาดเล็กที่บริหาร network, SQL connectivity, firewall, maintenance mode, diagnostics, backup visibility และ audit ของระบบสหกรณ์ ภ.6 ได้อย่างปลอดภัย ตรวจสอบย้อนหลังได้ และไม่ผูกกับ UI ใด UI หนึ่ง

## Design Concept
ระบบใช้แนวคิดเดียวกับ **Industrial Control Dashboard / Production Line Control Room**:
- มองเห็นสถานะระบบแบบรวมศูนย์
- แสดง process/state ของระบบแบบเข้าใจง่าย
- แจ้ง Alarm/Warning เมื่อสถานะเบี่ยงเบนจากค่าที่ควรเป็น
- ให้ผู้ดูแลสั่ง intervention ผ่านคำสั่งมาตรฐาน
- ตรวจสอบผลหลังดำเนินการ
- บันทึก evidence และ audit trail

เป้าหมายไม่ใช่เพียงการรันสคริปต์ แต่คือการทำให้โครงสร้างพื้นฐานเครือข่ายและ SQL ถูกบริหารเหมือนกระบวนการผลิตที่มี state, control, interlock, alarm และ recovery ที่ชัดเจน

## Team Roles
### Senior Software Engineer
รับผิดชอบ architecture, engine contracts, code quality, testing และ extensibility

### Senior Network Engineer
รับผิดชอบ topology, IP plan, routing, firewall, connectivity และ network safety

### Senior Process Engineer
รับผิดชอบ:
- นิยาม process flow และ operating state
- กำหนด Normal / Maintenance / Fault / Recovery workflow
- ออกแบบ interlock และ precondition ก่อน execute
- ออกแบบ Alarm/Warning classification
- กำหนด operator action และ recovery path
- ลดขั้นตอน manual ที่ซ้ำซ้อน
- ทำให้ dashboard สื่อสารสถานะได้แบบ control room
- วิเคราะห์ failure mode และ process deviation
- กำหนด KPI/health indicator ของระบบ

## Operating Principles

### 1. Document First
เอกสารกำหนด behavior และ contract ก่อน implementation

### 2. Engine First
Business/control logic อยู่ใน Engine Layer เท่านั้น

### 3. Replaceable UI
PowerShell CLI, WinForms, WPF, Web, REST, Mobile หรือ UI ในอนาคตต้องเป็น shell ที่เรียก Application/Engine contract เดียวกัน

### 4. Process-Oriented Control
ระบบต้องคิดเป็น state/process ไม่ใช่เป็นคำสั่งแยกส่วน เช่น Normal → Maintenance → Normal หรือ Fault → Diagnose → Recover → Verify

### 5. Safe Change
operation ที่เปลี่ยน network/firewall/system state ต้องเป็น Read → Validate → Plan → Apply → Verify → Commit Result และหาก Verify ไม่ผ่านต้องพยายาม Rollback

### 6. Interlock Before Action
คำสั่งที่มีผลต่อ network, firewall, SQL หรือ maintenance state ต้องตรวจ prerequisite/interlock ก่อน execute

### 7. Idempotency
คำสั่งซ้ำต้องไม่ทำให้ state เสีย

### 8. Least Privilege
เปิดสิทธิ์และ port เท่าที่จำเป็น SQL Server ต้องไม่ถูก expose สู่ Internet

### 9. Evidence Always
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
- Alarm/Warning state
- Process-state summary
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
- ระบบสามารถแสดง Normal/Warning/Fault/Maintenance state ได้
- operator สามารถเข้าใจ current state และ next safe action ได้จาก dashboard
- UI เปลี่ยนได้โดยไม่ย้าย business logic
