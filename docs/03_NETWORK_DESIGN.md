# 03 — Network Design

## Physical Topology
Internet → Router/Firewall → 16-port Switch → DB Server + Clients 1–5

ทุก host ใช้ NIC 1 ใบ

## Baseline Address Plan
- Router/Gateway: 192.168.1.1
- DB Server: 192.168.1.10
- Client 1: 192.168.1.101
- Client 2: 192.168.1.102
- Client 3: 192.168.1.103
- Client 4: 192.168.1.104
- Client 5: 192.168.1.105
- Subnet: 192.168.1.0/24

ค่าข้างต้นเป็น baseline และต้อง verify กับ network จริงก่อน deploy

## Traffic Policy

### Clients
- Client → DB Server: Allow ตาม SQL policy
- Client → Internet: Allow

### DB Server — Normal Mode
- DB Server ↔ LAN: Allow ตาม policy
- DB Server → Internet: Block โดยไม่มี default route/gateway ตาม baseline implementation
- Internet → SQL Server: Never expose directly

### DB Server — Maintenance Mode
- DB Server ↔ LAN: ต้องคงอยู่
- DB Server → Internet: Allow ชั่วคราว
- Windows Update / AnyDesk: ใช้ได้ตาม maintenance policy
- Internet → SQL Server: ยังคง Block

## Baseline Maintenance Mechanism
Engine อาจสลับ Internet reachability ด้วยการจัดการ default gateway โดยไม่ปิด NIC และไม่เปลี่ยน DB Server IP

ข้อกำหนด:
- ห้าม Disable NIC เพื่อปิด Internet
- ห้ามเปลี่ยน DB Server IP ระหว่าง Normal/Maintenance
- ก่อนลบหรือเพิ่ม route ต้องตรวจ interface/index และ current route
- หลังเปลี่ยนต้อง verify LAN และ SQL ก่อนรายงาน success

## Cabling
6 hosts ต้องใช้สาย LAN 6 เส้นเข้าหา switch และต้องมีสาย uplink switch ↔ router อีก 1 เส้น รวม baseline 7 เส้น

## SQL Connectivity
Baseline TCP port: 1433
Production สามารถเปลี่ยนเป็น fixed port อื่นได้ผ่าน config โดยเอกสารและ firewall policy ต้องอัปเดตตาม
