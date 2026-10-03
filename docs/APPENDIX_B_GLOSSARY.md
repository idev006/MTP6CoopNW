# Appendix B — Glossary

## Purpose
กำหนดคำศัพท์มาตรฐานเพื่อให้ทุกทีมและผู้เกี่ยวข้องใช้คำเดียวกันในความหมายเดียวกัน

## Terms

### Control Core
ส่วนกลางที่ถือ authoritative policy, orchestration, state aggregation และ audit

### Local Agent
background component บน managed host ที่รับ policy/command, enforce, reconcile และส่ง telemetry

### Engine
ส่วน logic ที่รับผิดชอบ domain behavior เช่น Policy, State, Scheduler, Alarm

### Module
capability unit ที่เพิ่ม/ลดความสามารถของระบบภายใต้ contract กลาง

### Adapter
ชั้นแปลง contract ไปเป็น platform-specific mechanism เช่น PowerShell/Windows Firewall

### Policy
ข้อกำหนดว่า desired behavior/state ของระบบควรเป็นอย่างไร

### Desired State
สถานะที่ policy ต้องการให้ host/subsystem เป็น

### Actual State
สถานะจริงที่อ่านได้จากระบบปฏิบัติการ/เครือข่าย/SQL

### Effective State
สถานะที่ได้หลัง resolve policy priority, schedule, override และ safety rule

### Interlock
เงื่อนไขที่ต้องผ่านก่อนอนุญาต state-changing action

### Reconciliation
กระบวนการเปรียบเทียบ Desired กับ Actual และทำให้ Actual converge เข้าหา Desired อย่างปลอดภัย

### Drift
ภาวะที่ Actual State เบี่ยงเบนจาก Desired State

### Heartbeat
สัญญาณ periodic จาก Agent เพื่อยืนยันว่า host/agent ยัง online และรายงาน state ล่าสุด

### Telemetry
ข้อมูลสถานะ/measurement/event ที่ Agent หรือ subsystem ส่งกลับ Control Core

### Alarm
เหตุการณ์ที่ต้องการ attention แบ่งระดับ INFO, WARNING, FAULT, CRITICAL

### Control Plane
ส่วนที่กำหนด policy/command/state โดยไม่ใช่ตัว resource ที่ถูกควบคุมโดยตรง

### Enforcement
การบังคับใช้ policy ที่ endpoint/Windows เช่น firewall/route

### Fail-safe
พฤติกรรมเมื่อเกิด failure ที่เลือกคงหรือเข้าสู่ state ที่ลดความเสี่ยงตาม policy

### Last-known Valid Policy
policy revision ล่าสุดที่ผ่าน validation และ Agent สามารถใช้ต่อได้เมื่อ Core ติดต่อไม่ได้

### Project-owned Rule
Windows Firewall/route/config object ที่ระบบสร้างและระบุ ownership ชัดเจน เช่น prefix MTP6CoopNW-

### Maintenance Mode
สถานะชั่วคราวที่อนุญาตความสามารถเพิ่มเติม เช่น Internet ของ DB Server ภายใต้ interlock และ verification
