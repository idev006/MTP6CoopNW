# 05 — Security Model

## Security Objectives
1. SQL Server ไม่ถูกเปิดตรงสู่ Internet
2. DB Server ไม่มี Internet egress ใน Normal Mode ตาม baseline
3. Maintenance Internet เป็น temporary controlled state
4. SQL inbound จำกัด trusted LAN/client sources
5. Administrator privilege ใช้เฉพาะ operation ที่จำเป็น
6. Secrets ไม่อยู่ใน source repository หรือ logs

## Trust Boundaries
- Internet: Untrusted
- Router/Firewall boundary
- Internal LAN: Controlled but not implicitly fully trusted
- DB Server: High-value asset
- Client hosts: Authorized application endpoints

## SQL Policy
Baseline trusted client IPs:
192.168.1.101–192.168.1.105

SQL inbound rule ต้อง:
- จำกัด TCP port ตาม config
- จำกัด remote source ตาม approved client list/subnet policy
- ไม่เปิด Public profile โดยไม่จำเป็น
- ห้าม router port-forward SQL จาก WAN

## Server Internet Policy
### Normal Mode
DB Server ต้องไม่มี default Internet path ตาม baseline design แต่ยังคง local subnet communication

### Maintenance Mode
อนุญาต Internet ชั่วคราวเพื่อ maintenance ที่ได้รับอนุญาต เช่น Windows Update หรือ AnyDesk

Maintenance Mode ไม่ได้หมายความว่า inbound SQL จาก WAN ถูกอนุญาต

## Remote Support
AnyDesk หรือ remote support software ต้อง:
- ใช้เฉพาะช่วง maintenance ตาม operational policy
- ใช้ authentication/security controls ของผลิตภัณฑ์
- ปิด/ออกจาก maintenance เมื่อเสร็จงาน

## Credentials
- Application ห้ามใช้ SQL sa เป็น runtime credential
- ใช้ dedicated least-privilege application identity
- Password/secret ห้าม commit ลง Git
- Config repository เก็บได้เฉพาะ non-secret configuration

## Logging
ห้าม log:
- SQL password
- AnyDesk credentials
- access tokens
- private keys

## Change Safety
Network/firewall destructive change ต้องมี backup snapshot ของ current state ใน memory/log ก่อน apply และต้อง verify หลัง apply
