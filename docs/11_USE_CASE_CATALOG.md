# 11 — Use Case Catalog

## Actors
- **Administrator** — ผู้ดูแลระบบที่มีสิทธิ์แก้ policy
- **Operator** — ผู้ใช้งาน dashboard ที่ได้รับสิทธิ์ดำเนินงานตาม role
- **Local Agent** — enforcement component บนแต่ละ host
- **Control Core** — authoritative policy/state controller
- **Scheduler** — process component ที่ trigger policy evaluation
- **Managed Client** — Client 1..N
- **Database Server** — SQL Server host

## UC-001 — Register Managed Host
**Goal:** เพิ่ม Client/Server เข้าสู่ระบบควบคุม  
**Preconditions:** Agent installed, identity configured  
**Flow:** Register → authenticate → assign host policy → self-test → heartbeat → ACTIVE  
**Success:** Host visible with policy revision and health

## UC-002 — Set Allowed Usage Schedule
**Goal:** กำหนดวัน/เวลาที่เครื่องอนุญาตใช้งาน  
**Inputs:** host, days, start, end, timezone, exceptions  
**Flow:** validate → save new policy revision → distribute → agent acknowledge → effective schedule displayed  
**Failure:** invalid/overlapping policy → reject

## UC-003 — Manual Enable/Disable Host
**Goal:** Override การอนุญาตใช้งาน  
**Flow:** authorize → capture reason → resolve priority → enforce → verify → publish → audit  
**Requirement:** control channel required for recovery must remain available

## UC-004 — Allow/Block Internet Per Host
**Goal:** เปลี่ยน Internet egress โดยยังรักษา required LAN/control traffic  
**Flow:** policy update → firewall/network plan → enforce → verify Internet + LAN → audit

## UC-005 — Allow/Block Database Access Per Client
**Goal:** เปิด/ปิดสิทธิ์ DB ราย Client โดยไม่หยุด DB Server  
**Flow:** update desired policy → client/server firewall strategy → enforce → TCP/DB verification → state publish

## UC-006 — Manage Port Policy
**Goal:** Allow/Deny TCP/UDP port ตาม host/direction/address  
**Flow:** validate ownership/conflict → version policy → enforce Windows Firewall → read-back verify → audit

## UC-007 — Scheduled Automatic Transition
**Goal:** เปลี่ยน effective state เมื่อถึงเวลาโดยไม่พึ่ง UI  
**Flow:** scheduler boundary → policy resolution → interlock → agent enforce → verify → event → audit

## UC-008 — Live/Near-Real-Time Dashboard
**Goal:** แสดง status ล่าสุดของทุก host  
**Data:** heartbeat, effective policy, actual state, alarms, SQL reachability, ports, last command  
**Baseline:** 2–5 second heartbeat on LAN

## UC-009 — Detect Policy Drift
**Goal:** ตรวจ actual state ไม่ตรง desired state  
**Flow:** periodic reconcile/readback → compare → alarm → optional approved converge → verify

## UC-010 — Enter DB Server Maintenance Mode
**Goal:** เปิด Internet ชั่วคราวให้ DB Server  
**Flow:** precheck → interlock → add approved Internet path → verify LAN/SQL/Internet → MAINTENANCE

## UC-011 — Exit DB Server Maintenance Mode
**Goal:** กลับสู่ Normal safe state  
**Flow:** remove managed Internet path → verify LAN/SQL → verify Internet blocked → NORMAL

## UC-012 — Run Host Diagnostics
Checks:
- agent
- NIC/IP/gateway
- router
- DNS
- Internet
- DB TCP
- firewall policy
- clock
- disk/service health

## UC-013 — Agent Offline
**Goal:** ระบุ stale/offline host และป้องกัน false status  
**Flow:** heartbeat timeout → state OFFLINE/STALE → alarm → retain last-known state with timestamp  
**Rule:** UI must distinguish last-known from current actual state

## UC-014 — Core Offline / Agent Autonomous Operation
**Goal:** Agent ยังคง policy ที่ valid ล่าสุด  
**Flow:** Core unreachable → enforce last-known policy → continue schedule if locally valid → queue audit/status → reconnect → reconcile

## UC-015 — Policy Rollback
**Goal:** กลับ policy revision ก่อนหน้าอย่างควบคุม  
**Flow:** choose revision → impact preview → authorize → create new rollback revision → distribute → verify  
**Rule:** never rewrite audit history

## UC-016 — Emergency Disable
**Goal:** บังคับ policy priority สูงสุดตาม approved emergency rule  
**Constraint:** must preserve approved management/recovery path where technically possible  
**Audit:** mandatory reason/operator/time

## UC-017 — Reboot/Restart Recovery
**Goal:** Agent กลับมาทำงานหลัง reboot โดย state ไม่หลุด  
**Flow:** Windows service start → load last-known policy → validate → reconcile → heartbeat

## UC-018 — Port/Firewall Conflict
**Goal:** ป้องกัน project rule ชน unmanaged rule  
**Flow:** detect effective conflict → do not delete foreign rule → alarm + diagnostics → operator decision

## UC-019 — Change Network Baseline
**Goal:** รองรับ policy ใหม่ เช่น subnet/gateway/client expansion  
**Flow:** SSOT change → impact analysis → staged rollout → test host → batch rollout → evidence

## UC-020 — Replace UI
**Goal:** เปลี่ยน CLI เป็น Desktop/Web โดยไม่เปลี่ยน Core behavior  
**Success:** same API/contracts and acceptance tests

## Use Case Priority
### Must Have v1
UC-001, 002, 003, 004, 005, 006, 007, 008, 009, 012, 013, 014, 017

### Must Have DB Server Operations
UC-010, 011

### Should Have
UC-015, 016, 018, 019

### Architectural Proof
UC-020
