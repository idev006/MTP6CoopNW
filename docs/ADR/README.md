# Architecture Decision Records (ADR)

ADR เป็นภาคผนวกของ Project Book ใช้บันทึกเหตุผลของการตัดสินใจด้านสถาปัตยกรรมที่มีผลระยะยาว

## Rules
- ADR ที่ Accepted แล้วไม่แก้เพื่อเปลี่ยนประวัติ ให้สร้าง ADR ใหม่เพื่อ supersede
- ทุก ADR ระบุ Context, Decision, Consequences และ Status
- การเปลี่ยน Engine boundary, state model, security boundary, deployment model, runtime/language boundary หรือ persistence strategy ต้องมี ADR

## Index
- [ADR-001 — Document First, Engine First, Replaceable UI](ADR-001-DOCUMENT-FIRST-ENGINE-FIRST.md)
- [ADR-002 — Industrial Control Dashboard and Process-Oriented State Model](ADR-002-INDUSTRIAL-CONTROL-DASHBOARD.md)
- [ADR-003 — Distributed Policy Enforcement with Per-Host Agent](ADR-003-DISTRIBUTED-POLICY-AGENT.md)
- [ADR-004 — Python Control Core with PowerShell Windows Adapters](ADR-004-PYTHON-CORE-POWERSHELL-ADAPTERS.md)
