# 19 — Agile Kanban Project Management

- Status: ACCEPTED
- Project: MTP6CoopNW
- Method: Agile Kanban
- Source of Truth: GitHub repository + Project Book + GitHub Issues

## 1. Purpose
กำหนดวิธีบริหารโครงการแบบ Agile Kanban ให้ทีม Software, Network, Process, Operations และ Project Owner เห็นงานชุดเดียวกัน ลดงานค้าง ลดการเริ่มหลายเรื่องพร้อมกัน และให้ทุกงาน trace ไปยัง requirement/use case/test/evidence ได้

## 2. Management Principles
1. Pull system — ทีมดึงงานเมื่อมี capacity ไม่ push งานจนล้น
2. Limit WIP — จำกัดงานที่กำลังทำ
3. Visualize flow — ทุกงานต้องอยู่ในสถานะที่ชัดเจน
4. Finish before start — ปิดงานเดิมก่อนเริ่มงานใหม่เมื่อทำได้
5. Small increments — แตกงานให้ตรวจสอบได้และย้อนกลับได้
6. Definition of Ready / Done — งานต้องพร้อมก่อนเริ่มและมีหลักฐานก่อน Done
7. Document First — requirement/ADR/contract ต้องมาก่อน code ที่เปลี่ยน behavior
8. Automation First — งานที่ทำซ้ำควรมี automated check
9. Evidence Always — state-changing feature ไม่มีคำว่า Done หากยังไม่มี verification evidence
10. Safety over speed — ห้ามเร่งงานจนข้าม interlock/test/recovery gate

## 3. Kanban Board Columns

### BACKLOG
งานที่ได้รับการยอมรับว่าอยู่ใน scope แต่ยังไม่พร้อมดึง

### READY
ผ่าน Definition of Ready และสามารถดึงทำได้ทันที

### IN PROGRESS
มีผู้รับผิดชอบและกำลังดำเนินการจริง

### REVIEW / VERIFY
implementation เสร็จแล้ว กำลัง code review, test, security/network/process review หรือ acceptance verification

### BLOCKED
มี dependency/decision/environment ปิดกั้นงาน ต้องบันทึก blocker และ next action

### DONE
ผ่าน Definition of Done และมี evidence

## 4. WIP Limits

Baseline:
- READY: ไม่เกิน 8 cards
- IN PROGRESS: ไม่เกิน 3 cards ทั้งทีม
- REVIEW / VERIFY: ไม่เกิน 3 cards
- BLOCKED: ไม่มีเป้าหมายสะสม; ต้อง review ทุกวันทำงาน

Role-specific guideline:
- Senior Software Engineer: active implementation สูงสุด 1–2 cards
- Senior Network Engineer: active design/integration สูงสุด 1 card
- Senior Process Engineer: active process/review สูงสุด 1 card

งานเร่งด่วนห้ามทำให้ WIP limit ถูกละเลยโดยไม่มีเหตุผลที่บันทึกไว้

## 5. Classes of Service

### STANDARD
งานปกติ ใช้ FIFO ภายใน priority เดียวกัน

### FIXED DATE
มีวันกำหนดจริง เช่น maintenance window หรือ rollout ที่อนุมัติแล้ว

### EXPEDITE
ใช้เฉพาะ incident/security/safety ที่ต้องแก้ทันที
- WIP limit อนุญาตให้แทรกได้ 1 ใบ
- ต้องมีเหตุผล
- หลังเหตุการณ์ต้องทำ retrospective/update SSOT

### INTANGIBLE / TECH DEBT
งานลดความเสี่ยงทางเทคนิค เช่น refactor, test coverage, tooling
ต้องไม่ถูกเลื่อนอย่างไม่มีกำหนด

## 6. Priority Model
- P0: production/security/safety incident
- P1: blocks current critical path
- P2: normal committed feature
- P3: improvement/optional

Priority ไม่แทน dependency; งาน P1 ที่ยังไม่ Ready ห้ามดึงข้าม prerequisite แบบทำลาย architecture

## 7. Card / Issue Template

Every GitHub Issue should contain:

- Kanban Status
- Priority
- Class of Service
- Owner/Role
- Objective
- Related Requirement IDs
- Related Use Case IDs
- Related ADR
- Dependencies
- Scope
- Out of Scope
- Acceptance Criteria
- Test Plan
- Evidence Required
- Risks / Rollback
- Blockers
- Exit Criteria

## 8. Definition of Ready (DoR)
งานเข้าสู่ READY เมื่อ:
- objective ชัด
- requirement/use case ระบุได้
- scope และ out-of-scope ชัด
- dependency หลักพร้อม
- contract/schema ที่จำเป็นถูกกำหนด
- test approach รู้ล่วงหน้า
- security/network impact ถูกระบุ
- rollback/recovery expectation ถูกระบุถ้า state-changing
- ไม่มี decision ใหญ่ที่ยังค้างโดยไม่บันทึก

## 9. Definition of Done (DoD)
งานเป็น DONE เมื่อ:
- implementation ตรง SSOT
- automated tests ที่เกี่ยวข้องผ่าน
- static analysis/lint/type checks ผ่าน
- integration/acceptance ผ่านเมื่อจำเป็น
- monitoring/structured errors พร้อม
- docs/traceability อัปเดต
- no secrets/runtime artifacts committed
- rollback/recovery documented
- evidence captured
- reviewer ที่เกี่ยวข้องยอมรับ

## 10. Flow Policies

### Pull
ดึงงานจาก READY เมื่อ WIP มีช่องและ dependency พร้อม

### Block
เมื่อ block:
1. ย้ายเป็น BLOCKED
2. ระบุ blocker
3. ระบุ owner ของการปลด blocker
4. ระบุ next action
5. ห้ามปล่อยเงียบ

### Review
งานที่ code เสร็จไม่ได้แปลว่า Done ต้องผ่าน REVIEW / VERIFY

### Reopen
ถ้า acceptance/evidence พบ defect ให้กลับ IN PROGRESS พร้อมบันทึกเหตุผล

## 11. Cadence

Kanban ไม่บังคับ sprint แต่ใช้ cadence เบา ๆ:

### Daily Flow Review
สั้น ๆ:
- มีอะไร BLOCKED
- WIP เกินหรือไม่
- งานใดควร finish ก่อน start ใหม่
- มี incident/priority change หรือไม่

### Weekly Replenishment
เลือกงานจาก BACKLOG → READY ตาม capacity/dependency

### Weekly/On-demand Technical Review
SSE/SNE/SPE ทบทวน ADR, contract, safety, process change

### Release Review
ก่อน package/release:
- acceptance
- evidence
- rollback
- release notes
- config/schema compatibility

### Monthly Flow Review
ดู metric และปรับ process ไม่ใช่ประเมินบุคคล

## 12. Kanban Metrics
ใช้เพื่อปรับระบบงาน ไม่ใช้เป็นคะแนนผลงานรายบุคคล

- Lead Time: Backlog/Ready → Done
- Cycle Time: In Progress → Done
- Throughput: cards Done ต่อช่วงเวลา
- WIP
- Blocked Time
- Rework/Reopen rate
- Defect escape
- Test pass rate
- Deployment success rate

## 13. Epic / Milestone Flow

Backlog หลักอ้างอิง Implementation Backlog:

- M0 Repository Bootstrap
- M1 Contracts & Configuration
- M2 Fake Runtime & Simulation
- M3 Observability Foundation
- M4 Read-Only PowerShell Adapters
- M5 Read-Only Local Agent
- M6 Central Core & Single Point Monitoring
- M7 Policy & Scheduler
- M7A State / Stage / Cycle Engines
- M8 Planner / Dry Run
- M9 Enforcement Adapters
- M10 Reconciliation & Drift
- M11 Central User-Friendly Control UI
- M12 Packaging & Operations

## 14. Initial Critical Path

```text
M0
 ↓
M1
 ↓
M2
 ├────────→ M3
 │           ↓
 │          M5 ← M4
 │           ↓
 └────────→ M6
             ↓
            M7
             ↓
            M7A
             ↓
            M8
             ↓
            M9
             ↓
            M10
             ↓
            M11
             ↓
            M12
```

Read-only and simulation capability must exist before destructive enforcement.

## 15. Branch / PR Policy
Baseline:
- main = stable SSOT/integrated line
- implementation work should use focused branches
- PR should map to one primary Issue whenever practical
- small PR preferred
- architecture changes require ADR before merge
- no direct destructive-feature implementation without tests/review

## 16. Release Policy
Use incremental versioned releases:
- pre-alpha: contracts/simulation
- alpha: read-only agent/core
- beta: controlled enforcement on test hosts
- release candidate: site acceptance
- production: approved rollout

Versioning details will be locked before first package release.

## 17. Management Dashboard
Project management view should show:
- cards by Kanban status
- WIP
- blocked cards and blocked age
- current critical path
- test/CI status
- latest release/package
- open risks
- milestone progress

Operational system dashboard and Project Kanban dashboard are separate concerns.

## 18. Change Management
Policy/business requirement changes enter BACKLOG first unless P0 incident.
Architecture changes require SSOT/ADR before implementation card becomes READY.

## 19. First Replenishment Decision
Initial READY candidates:
1. M0 Repository Bootstrap
2. M1 Contracts & Configuration only after M0 foundation is available

Initial IN PROGRESS target:
- M0 only

This deliberately limits WIP while the foundation is being established.
