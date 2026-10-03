# 07 — Testing & Evidence

## Principle
ไม่มีคำว่า DONE สำหรับ state-changing feature หากไม่มี verification evidence

## Test Layers

### Unit Tests
ทดสอบ pure logic เช่น:
- config validation
- state classification
- desired-state planning
- idempotency decisions
- result/error mapping

### Integration Tests
บน Windows test environment:
- adapter discovery
- route/gateway manipulation
- firewall rule convergence
- SQL port probe
- privilege detection

### Acceptance Tests
ขั้นต่ำ:
1. Client 1–5 เข้าถึง DB Server ได้
2. Client 1–5 ออก Internet ได้
3. DB Server Normal Mode เข้าถึง Client/LAN ได้
4. DB Server Normal Mode ออก Internetไม่ได้ตาม policy
5. Enable Maintenance แล้ว DB Server ออก Internetได้
6. Enable Maintenance แล้ว SQL/LAN ยังทำงาน
7. Disable Maintenance แล้ว Internet ถูกตัดแต่ SQL/LAN ยังทำงาน
8. SQL port จาก unapproved source ถูก block ตาม policy
9. Re-run Enable/Disable operation แล้ว state ไม่เสีย
10. Restart/reboot แล้วระบบสามารถ classify current state ได้ถูกต้อง

## Evidence Format
แต่ละ milestone ควรเก็บ:
- date/time
- host role
- software/version
- test case ID
- expected result
- actual result
- PASS/FAIL
- sanitized command/output/log reference

## Safety Test Rule
ห้ามทดสอบ failure mode ที่อาจทำ production network ขาดโดยไม่มี recovery plan

## Definition of Done
Feature พร้อมใช้งานเมื่อ:
- SSOT updated
- implementation matches contract
- tests pass
- evidence recorded
- no secrets in repo/log
- rollback/recovery behavior documented
