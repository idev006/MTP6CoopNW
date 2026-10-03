# ADR-002 — Industrial Control Dashboard and Process-Oriented State Model

- Status: Accepted
- Date: 2026-10-03

## Context
ระบบ MTP6CoopNW ต้องบริหารโครงสร้างพื้นฐานที่มีหลายองค์ประกอบ ได้แก่ Network, SQL Server, Firewall, Client, Internet, Backup และ Maintenance workflow หากออกแบบเป็นชุดปุ่มหรือสคริปต์แยกกัน ผู้ดูแลจะต้องตีความสถานะเองและมีความเสี่ยงสั่งงานผิดลำดับ

แนวคิดจากระบบสายการผลิตของโรงงานเหมาะสมกว่า เพราะระบบดังกล่าวมองทุกองค์ประกอบเป็น process ที่มี state, interlock, alarm, operator action และ recovery sequence

## Decision
1. Adopt แนวคิด Industrial Control Dashboard / Control Room
2. เพิ่ม Process/State Layer ระหว่าง Application และ Engine
3. เพิ่ม StateEngine และ AlarmEngine
4. ทุก state-changing command ต้องผ่าน interlock
5. Dashboard ต้องแสดง overall state, subsystem state, alarms และ allowed next actions
6. Fault ต้องมี diagnose/recovery workflow ไม่ใช่แค่ error message
7. Audit log ทำหน้าที่เทียบเท่า lightweight historian สำหรับเหตุการณ์และ state transition
8. Senior Process Engineer เป็นบทบาทหลักในการออกแบบ state flow, interlock, alarm และ recovery

## Consequences
### Positive
- operator เข้าใจสถานะได้เร็ว
- ลด human error
- workflow ซ้ำ ๆ สามารถ standardize
- ง่ายต่อการสร้าง dashboard แบบ control room
- fault analysis และ recovery มีแบบแผน
- สามารถเพิ่ม automation ในอนาคตโดยไม่ทำลาย architecture

### Trade-offs
- ต้องนิยาม state และ alarm taxonomy ให้ชัด
- implementation ซับซ้อนกว่าสคริปต์ command-based
- ต้องมี test สำหรับ transition/interlock เพิ่มขึ้น

## Architectural Impact
เดิม:
UI → Application → Engine → Infrastructure

ใหม่:
UI → Application/Control → Process/State → Engine → Infrastructure

## Enforcement
UI ห้ามเรียก low-level infrastructure operation เพื่อ bypass State/Interlock policy
