# MTP6CoopNW

ระบบควบคุมและบริหารจัดการเครือข่ายและการเข้าถึง SQL Server สำหรับระบบสหกรณ์ ภ.6

> **Project Rule:** Document First → Implementation Second → Evidence Always

Repository นี้เป็น **Single Source of Truth (SSOT)** ของโครงการ และจัดเอกสารตามแนวคิด **“หนังสือโครงการ”** เพื่อให้ทุกฝ่ายอ่านและอ้างอิงโครงสร้างเดียวกัน

## หนังสือหลักของโครงการ

อ่านจาก: [MTP6CoopNW Project Book](docs/BOOK.md)

หนังสือหลักประกอบด้วย:
- ชื่อและเป้าหมายของหนังสือ
- วัตถุประสงค์
- สารบัญ
- บทต่าง ๆ ของโครงการ
- หัวข้อหลัก/หัวข้อย่อยของแต่ละบท
- ภาคผนวก
- ADR
- Glossary
- Traceability Matrix

## Project Concept

MTP6CoopNW เป็น **Distributed Infrastructure Control System** ที่ใช้แนวคิด Industrial Control Dashboard / Production Line Control Room

Technology baseline:
- **Python:** Control Core, Policy/State/Scheduler, Agent orchestration, Telemetry/API
- **PowerShell:** Windows Network/Firewall/Service/SQL operational adapters
- **UI:** replaceable shell
- **Documentation:** Project Book + ADR + diagrams
- **Transport:** replaceable authenticated contract

## Document Governance

1. README เป็นหน้าปกและทางเข้าสู่หนังสือ
2. `docs/BOOK.md` เป็นสารบัญและโครงสร้างหนังสืออย่างเป็นทางการ
3. 1 บท = 1 ไฟล์หลักเป็นค่าเริ่มต้น
4. บทที่ใหญ่สามารถแตกเป็นหลายไฟล์ย่อยได้
5. ห้าม duplicate normative rule โดยไม่จำเป็น
6. Requirement/Architecture เปลี่ยนก่อน Implementation
7. Architectural decision ต้องบันทึก ADR
8. ทุก capability ต้อง trace ไปยัง Requirement → Use Case → Module/Adapter → Test/Evidence
9. Production behavior ที่ไม่ตรง SSOT ถือเป็น defect หรือ unapproved change

## Current Network Baseline

- Router/Gateway: `192.168.1.1`
- DB Server: `192.168.1.10`
- Clients: `192.168.1.101` – `192.168.1.105`
- Subnet: `192.168.1.0/24`
- SQL TCP Port baseline: `1433`
- Switch: 16-port
- Physical hosts: 1 DB Server + 5 Clients
- NIC: 1 per host

> ค่าเหล่านี้เป็น baseline design และต้องผ่าน site verification ก่อน production deployment.
