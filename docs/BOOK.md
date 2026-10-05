# MTP6CoopNW Project Book

## ชื่อหนังสือ
**MTP6CoopNW — Distributed Network & SQL Infrastructure Control System**

เอกสารกำกับโครงการระบบควบคุมเครือข่าย การเข้าถึงฐานข้อมูล และสถานะเครื่องลูกข่ายแบบรวมศูนย์ สำหรับระบบสหกรณ์ ภ.6

## เป้าหมายของหนังสือ
ใช้เป็นเอกสารอ้างอิงหลักของโครงการ เพื่อให้ผู้บริหาร ทีม Software, Network, Process, Operations และผู้พัฒนาหรือ AI ที่เข้ามาทำงานภายหลัง เข้าใจเป้าหมาย ขอบเขต สถาปัตยกรรม กระบวนการทำงาน กติกาความปลอดภัย Use Case และวิธีเปลี่ยนแปลงระบบตรงกัน

## วัตถุประสงค์ของหนังสือ
1. กำหนดขอบเขตและเป้าหมายโครงการอย่างชัดเจน
2. กำหนดคำศัพท์และแนวคิดร่วมของทุกทีม
3. กำหนด Architecture และ Technology Boundary
4. กำหนด Policy, State, Process, Interlock และ Alarm
5. กำหนด Engine, Module และ Adapter Contract
6. กำหนด Use Case และลำดับการทำงาน
7. กำหนด Network/Security Baseline
8. กำหนดวิธีทดสอบและหลักฐาน
9. กำหนดบทบาท ความรับผิดชอบ และการส่งมอบงาน
10. กำหนด Change Control เพื่อป้องกัน scope creep
11. ทำให้ implementation ทุกชิ้น trace กลับมายัง requirement และ use case ได้
12. ทำให้ผู้พัฒนาสามารถเปลี่ยน UI/Adapter/Module ได้โดยไม่ทำลาย Core semantics

## วิธีอ่าน
- ผู้บริหาร: บท 1, 2, 3, 14
- Software Engineer: บท 2, 3, 5, 10, 11, 12
- Network Engineer: บท 4, 5, 6, 10, 12
- Process Engineer: บท 2, 3, 11, 12, 13
- Operations: บท 6, 7, 8, 11, 12, 13
- Tester/QA: บท 2, 8, 11, 12
- AI/Developer ใหม่: อ่าน README → หนังสือเล่มนี้ → ADR

# สารบัญหนังสือ

## ภาคที่ I — Foundation

### บทที่ 1 — Project Charter
ไฟล์: [00_PROJECT_CHARTER.md](00_PROJECT_CHARTER.md)

หัวข้อหลัก:
- Mission
- Design Concept
- Team Roles
- Operating Principles
- Scope
- Success Criteria

หัวข้อย่อยสำคัญ:
- Document First
- Engine First
- Replaceable UI
- Process-Oriented Control
- Interlock
- Evidence Always

### บทที่ 2 — Requirements
ไฟล์: [01_REQUIREMENTS.md](01_REQUIREMENTS.md)

หัวข้อหลัก:
- Functional Requirements
- Per-host policies
- Local Agent
- Central Control Plane
- Minimum Use Cases
- Non-functional Requirements

หัวข้อย่อยสำคัญ:
- Schedule
- Enable/Disable
- Internet control
- DB access control
- Port policy
- Near-real-time state
- Fail-safe behavior

### บทที่ 3 — Architecture
ไฟล์: [02_ARCHITECTURE.md](02_ARCHITECTURE.md)

หัวข้อหลัก:
- Architectural Style
- Control-Room Concept
- Distributed Control Model
- Layer Model
- Policy/State Model
- Real-time communication
- Design Constraints

หัวข้อย่อยสำคัญ:
- Central Control Core
- Local Agent
- Desired vs Actual State
- Policy Priority
- State Transition
- UI independence

## ภาคที่ II — Infrastructure & Security

### บทที่ 4 — Network Design
ไฟล์: [03_NETWORK_DESIGN.md](03_NETWORK_DESIGN.md)

หัวข้อหลัก:
- Physical topology
- Address plan
- Traffic policy
- Maintenance mechanism
- Cabling
- SQL connectivity

### บทที่ 5 — Engine & Module Contracts
ไฟล์: [04_ENGINE_CONTRACTS.md](04_ENGINE_CONTRACTS.md)

หัวข้อหลัก:
- Common contracts
- Policy/Scheduler
- Network/Firewall/SQL
- Access Control
- Agent
- Telemetry
- Audit
- Communication

### บทที่ 6 — Security Model
ไฟล์: [05_SECURITY_MODEL.md](05_SECURITY_MODEL.md)

หัวข้อหลัก:
- Security objectives
- Trust boundaries
- SQL policy
- Internet policy
- Remote support
- Credentials
- Logging
- Change safety

## ภาคที่ III — Operation & Quality

### บทที่ 7 — Operations
ไฟล์: [06_OPERATIONS.md](06_OPERATIONS.md)

หัวข้อหลัก:
- Normal state
- Maintenance
- Windows Update
- Remote support
- Failure handling
- Configuration change

### บทที่ 8 — Testing & Evidence
ไฟล์: [07_TESTING_AND_EVIDENCE.md](07_TESTING_AND_EVIDENCE.md)

หัวข้อหลัก:
- Unit tests
- Integration tests
- Acceptance tests
- Evidence format
- Safety testing
- Definition of Done

### บทที่ 9 — Roadmap
ไฟล์: [08_ROADMAP.md](08_ROADMAP.md)

หัวข้อหลัก:
- Documentation baseline
- Core/contracts
- Agent/telemetry
- Policy/scheduler
- Enforcement
- Process control
- Maintenance
- Dashboard
- Production hardening
- Rollout

## ภาคที่ IV — Project Coordination & Detailed Design

### บทที่ 10 — Project Definition & Scope
ไฟล์: [09_PROJECT_DEFINITION.md](09_PROJECT_DEFINITION.md)

หัวข้อหลัก:
- Goal
- Objectives
- In Scope
- Out of Scope
- Constraints
- Success Measures
- Scope Change Rule

### บทที่ 11 — Adapter Catalog
ไฟล์: [10_ADAPTER_CATALOG.md](10_ADAPTER_CATALOG.md)

หัวข้อหลัก:
- Adapter principles
- Technology baseline
- Required adapters
- Adapter contract rules
- PowerShell contract
- Replacement rules

### บทที่ 12 — Use Case Catalog
ไฟล์: [11_USE_CASE_CATALOG.md](11_USE_CASE_CATALOG.md)

หัวข้อหลัก:
- Actors
- Host registration
- Scheduling
- Manual override
- Internet/DB/Port control
- Dashboard
- Drift
- Maintenance
- Offline/reconnect
- Recovery
- Network baseline change

### บทที่ 13 — Workflows, Pipelines & UML
ไฟล์: [12_WORKFLOWS_AND_DIAGRAMS.md](12_WORKFLOWS_AND_DIAGRAMS.md)

หัวข้อหลัก:
- System Context
- Component Diagram
- Policy Change Pipeline
- Software Delivery Pipeline
- Sequence Diagrams
- State Diagrams
- Reconciliation Loop
- Deployment View
- Alarm Flow

### บทที่ 14 — Team & RACI
ไฟล์: [13_TEAM_AND_RACI.md](13_TEAM_AND_RACI.md)

หัวข้อหลัก:
- Roles
- RACI
- Collaboration rules
- Handoff checklists
- Artifact priority

### บทที่ 15 — Scope & Change Control
ไฟล์: [14_SCOPE_AND_CHANGE_CONTROL.md](14_SCOPE_AND_CHANGE_CONTROL.md)

หัวข้อหลัก:
- Change classes
- Change workflow
- Mandatory impact questions
- Scope guardrails
- Acceptance rule

### บทที่ 16 — Implementation Plan, Configuration, Monitoring & Testability
ไฟล์: [15_IMPLEMENTATION_PLAN.md](15_IMPLEMENTATION_PLAN.md)

หัวข้อหลัก:
- Single Point of Control / Single Pane of Glass
- User-friendly control
- TOML-first configuration
- Monitoring & Observability
- Test-friendly architecture
- CI pipeline
- Work packages
- Definition of Ready / Done

### บทที่ 17 — Implementation Backlog & Build Order
ไฟล์: [16_IMPLEMENTATION_BACKLOG.md](16_IMPLEMENTATION_BACKLOG.md)

หัวข้อหลัก:
- Milestones M0–M12
- Build order
- Fake-first development
- Read-only before enforcement
- Dry-run planner
- Reconciliation
- Central UI
- Packaging

### บทที่ 18 — Automated Testing & Monitoring Strategy
ไฟล์: [17_AUTOMATED_TESTING_AND_MONITORING.md](17_AUTOMATED_TESTING_AND_MONITORING.md)

หัวข้อหลัก:
- Testing pyramid
- Python/Pester tooling
- Fake/Mock/Windows integration levels
- Health model
- CI workflow separation
- Evidence automation
- Production monitoring
- Diagnostics bundle


### บทที่ 20 — Agile Kanban Project Management
ไฟล์: [19_AGILE_KANBAN_PROJECT_MANAGEMENT.md](19_AGILE_KANBAN_PROJECT_MANAGEMENT.md)

หัวข้อหลัก:
- Kanban Board Columns
- WIP Limits
- Classes of Service
- Priority
- Definition of Ready / Done
- Flow Policies
- Cadence
- Kanban Metrics
- Epic / Milestone Flow
- Critical Path
- Branch / PR Policy
- Release Policy

## ภาคผนวก

### บทที่ 21 — Architecture Constitution & Software Engineering Standards
ไฟล์: [20_ARCHITECTURE_CONSTITUTION.md](20_ARCHITECTURE_CONSTITUTION.md)

หัวข้อหลัก:
- Canonical Layer Model
- Engine API / Application Service API
- UI Facade / Presenter / ViewModel
- Dependency Rule
- Ports & Adapters
- Design Pattern Policy
- Typed Contract Standard
- Command/Query separation
- Event-driven presentation
- Automated test layers L0–L7
- UI as Replaceable Mask
- Architecture Definition of Done

## เอกสารควบคุมการพัฒนาและหลักฐานปัจจุบัน

- [23_MASTER_USE_CASE_CAPABILITY_MATRIX.md](23_MASTER_USE_CASE_CAPABILITY_MATRIX.md) — SSOT ของ 72 Use Cases
- [24_AGILE_KANBAN_72_USE_CASE_COMPLETION.md](24_AGILE_KANBAN_72_USE_CASE_COMPLETION.md) — Kanban/Engineering completion
- [25_UI_FACADE_ENGINE_E2E_ACCEPTANCE.md](25_UI_FACADE_ENGINE_E2E_ACCEPTANCE.md) — UI Facade → Engines headless acceptance
- [26_LAYER_READINESS_MATRIX.md](26_LAYER_READINESS_MATRIX.md) — readiness แยก Architecture / Sandbox / Integration / Production ราย layer
- [27_DESKTOP_UI_UX_PYSIDE6.md](27_DESKTOP_UI_UX_PYSIDE6.md) — Desktop UI/UX baseline ด้วย PySide6 และ Facade-driven architecture
- [use_case_catalog.json](use_case_catalog.json) — machine-readable use-case catalog
- [use_case_evidence.json](use_case_evidence.json) — machine-readable evidence mapping

### Appendix A — Architecture Decision Records
ไฟล์: [ADR/README.md](ADR/README.md)

ใช้บันทึกเหตุผลของการตัดสินใจ architecture ที่สำคัญและประวัติการเปลี่ยนแปลงแนวทาง

### Appendix B — Glossary
สถานะ: Planned

จะรวมคำศัพท์ เช่น:
- Core
- Agent
- Module
- Adapter
- Policy
- Desired State
- Actual State
- Interlock
- Alarm
- Reconciliation
- Drift
- Heartbeat
- Control Plane
- Enforcement

### Appendix C — Traceability Matrix
สถานะ: Active

แหล่งอ้างอิงหลัก:
- 23_MASTER_USE_CASE_CAPABILITY_MATRIX.md
- use_case_catalog.json
- use_case_evidence.json

จะเชื่อม:
Requirement → Use Case → Module/Adapter → Test Case → Evidence

## กติกาการแบ่งไฟล์
1. 1 บท = 1 ไฟล์หลักเป็นค่าเริ่มต้น
2. หากบทใหญ่เกินไป ให้แตกเป็นโฟลเดอร์ย่อย เช่น `chapter-12/`
3. ไฟล์ย่อยต้องมี index ของบท
4. ไม่ duplicate normative rule ข้ามบทโดยไม่จำเป็น
5. ใช้ลิงก์อ้างอิงแทนการ copy เนื้อหา
6. ทุกไฟล์ต้องมีชื่อเรื่องและ purpose ชัดเจน
7. หัวข้อระดับใหญ่ใช้เลขลำดับเพื่อค้นหาและอ้างอิงง่าย
8. Diagram อยู่ใกล้เนื้อหาที่อธิบาย diagram นั้น
9. ADR ไม่ถือเป็นบท แต่เป็นภาคผนวกประวัติการตัดสินใจ
10. README เป็นหน้าปก/ทางเข้า ไม่ใช่ที่เก็บรายละเอียดทุกอย่าง

## Document Status
เอกสารทุกบทควรมีสถานะหนึ่งใน:
- DRAFT
- REVIEW
- ACCEPTED
- SUPERSEDED

เมื่อ implementation เริ่มจริง ควรเพิ่ม metadata ที่ต้นบท:
- Status
- Owner
- Last Reviewed
- Related ADR
- Related Requirement IDs
