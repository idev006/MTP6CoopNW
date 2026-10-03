# ADR-001 — Document First, Engine First, Replaceable UI

- Status: Accepted
- Date: 2026-10-03

## Context
โครงการต้องเริ่มจาก PowerShell/Windows environment แต่ต้องไม่ถูกผูกกับ UI หรือ script เดียว เพราะในอนาคตอาจใช้ CLI, desktop GUI, web UI, REST API หรือ platform อื่น และ network/firewall operations มีความเสี่ยงหาก logic กระจายอยู่หลาย UI

## Decision
1. GitHub repository นี้เป็น SSOT ของโครงการ
2. ใช้ Document First → Implementation Second → Evidence Always
3. Business/control logic อยู่ใน Engine Layer
4. UI เป็น replaceable shell และห้าม duplicate control logic
5. Engine คืน structured result ที่ไม่ผูกกับ UI
6. State-changing operations ต้อง Read → Validate → Plan → Apply → Verify และ rollback เมื่อเหมาะสม
7. Operations ต้อง idempotent เท่าที่ทำได้
8. Architectural change สำคัญต้องบันทึก ADR ใหม่

## Consequences
### Positive
- UI เปลี่ยนได้โดยไม่ rewrite core logic
- behavior สอดคล้องกันทุก frontend
- ทดสอบ Engine แยกจาก UI ได้
- ลดความเสี่ยงจาก network/firewall script กระจัดกระจาย
- AI หรือ developer รายใหม่มีจุดอ้างอิงเดียว

### Trade-offs
- ต้องลงทุนออกแบบ contract/config/test ก่อนสร้าง UI
- งานเล็กบางอย่างอาจมีโครงสร้างมากกว่าสคริปต์แบบตรงไปตรงมา

## Enforcement
PR/commit ที่เปลี่ยน behavior แต่ไม่อัปเดตเอกสารที่เกี่ยวข้องถือว่ายังไม่ complete ตาม Definition of Done
