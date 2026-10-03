# ADR-003 — Distributed Policy Enforcement with Per-Host Agent

- Status: Accepted
- Date: 2026-10-03

## Context
โครงการต้องรองรับการควบคุมรายเครื่อง ได้แก่ schedule, host enable/disable, Internet allow/deny, database allow/deny, port policy และ near-real-time status

หากให้ UI หรือ Central Core ใช้ remote command ไปแก้แต่ละเครื่องโดยตรงทุกครั้ง จะเกิด coupling สูง, schedule จะพึ่ง availability ของ UI/Core, status tracking ไม่ต่อเนื่อง และ recovery ยาก

## Decision
1. ใช้ Central Control Plane เป็น authoritative desired-policy/state source
2. แต่ละ managed host มี Local Agent/Enforcement Engine
3. Agent ทำงานแบบ background และ enforce last-known valid policy ได้เมื่อ UI ปิด
4. Agent ส่ง heartbeat/status/event กลับ Control Core
5. Schedule evaluation และ enforcement ต้องไม่พึ่ง UI
6. Internet, DB access และ port policy ถูกบังคับใช้ผ่าน project-owned mechanisms/rules
7. ใช้ desired-state reconciliation เพื่อแก้ drift
8. Transport ระหว่าง Core-Agent ต้อง replaceable และ authenticated
9. Near-real-time baseline target คือ heartbeat 2–5 วินาทีบน LAN โดยไม่รับประกัน hard real-time
10. Policy ต้อง versioned และทุก transition ต้อง audit

## Consequences

### Positive
- รองรับ policy รายเครื่องได้เป็นระบบ
- schedule ทำงานต่อแม้ Dashboard ไม่เปิด
- UI แสดง actual status ได้ต่อเนื่อง
- ลดการพึ่ง remote PowerShell แบบ ad-hoc
- รองรับ drift detection/reconciliation
- เพิ่ม Client ในอนาคตได้ง่ายกว่า architecture แบบ centralized script-only

### Trade-offs
- ต้องติดตั้งและดูแล Agent บนแต่ละเครื่อง
- ต้องออกแบบ secure command channel
- ต้องจัดการ agent offline/stale state
- ต้องมี policy versioning และ clock/timezone discipline

## Safety
Loss of UI/Core connectivity must not automatically disable existing security policy. Agent uses fail-safe last-known valid policy until a newer authenticated policy is available, subject to explicitly documented emergency behavior.
