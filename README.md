# MTP6CoopNW

ระบบควบคุมและบริหารจัดการเครือข่ายสำหรับระบบสหกรณ์ ภ.6

> **Project Rule:** Document First → Implementation Second → Evidence Always

Repository นี้เป็น **Single Source of Truth (SSOT)** ของโครงการ ทั้ง requirement, architecture, network design, engine contracts, security policy, operations, testing และ roadmap

## เป้าหมาย

- ใช้ SQL Server บน Database Server แยกเครื่อง
- Database Server 1 เครื่อง + Client 5 เครื่อง
- ทุกเครื่องมี Network Card 1 ใบ
- Client ใช้งาน Internet ได้ตามปกติ
- Database Server อยู่ใน LAN ตลอดเวลา
- Database Server ไม่ออก Internet โดยค่าเริ่มต้น
- เปิด Internet ของ Database Server เฉพาะ Maintenance Mode เช่น Windows Update หรือ AnyDesk
- SQL Server ต้องไม่เปิดตรงสู่ Internet
- Core logic อยู่ใน Engine Layer และ UI เป็น replaceable shell

## SSOT Document Map

1. [Project Charter](docs/00_PROJECT_CHARTER.md)
2. [Requirements](docs/01_REQUIREMENTS.md)
3. [Architecture](docs/02_ARCHITECTURE.md)
4. [Network Design](docs/03_NETWORK_DESIGN.md)
5. [Engine Contracts](docs/04_ENGINE_CONTRACTS.md)
6. [Security Model](docs/05_SECURITY_MODEL.md)
7. [Operations](docs/06_OPERATIONS.md)
8. [Testing & Evidence](docs/07_TESTING_AND_EVIDENCE.md)
9. [Roadmap](docs/08_ROADMAP.md)
10. [ADR Index](docs/ADR/README.md)

## Governance

1. อ่านเอกสาร SSOT ที่เกี่ยวข้องก่อนแก้ implementation
2. ถ้าพฤติกรรมใหม่ยังไม่มีในเอกสาร ให้แก้เอกสารก่อน
3. Implementation ต้องสอดคล้องกับ Engine Contract
4. ทุก operation ที่เปลี่ยน network/firewall ต้อง Validate → Plan → Apply → Verify → Rollback on failure
5. UI ห้ามมี business logic สำคัญ
6. การเปลี่ยน architecture ต้องมี ADR
7. ทุก milestone ต้องมี evidence ของ test

## Current Baseline

- Router/Gateway: 192.168.1.1
- DB Server: 192.168.1.10
- Clients: 192.168.1.101 – 192.168.1.105
- Subnet: 192.168.1.0/24
- SQL TCP Port baseline: 1433
- Switch: 16-port
- Physical hosts: 1 DB Server + 5 Clients
- NIC: 1 per host

> ค่าเหล่านี้เป็น baseline design และต้องผ่าน site verification ก่อน production deployment.
