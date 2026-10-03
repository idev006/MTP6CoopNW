# 06 — Operations

## Normal Daily State
DB Server:
- Static LAN IP ตาม approved config
- SQL service available to authorized clients
- No Internet egress/default gateway ตาม baseline

Clients:
- LAN access to DB Server
- Internet access through router

## Start Maintenance Mode
1. Confirm operator has Administrator privilege
2. Read current network/firewall/SQL state
3. Verify DB Server LAN IP and target NIC
4. Verify clients/SQL baseline where practical
5. Add/restore approved default gateway
6. Verify router reachability
7. Verify Internet/DNS
8. Re-verify SQL/LAN connectivity
9. Record audit result

หาก LAN/SQL verification ล้มเหลว ให้หยุดและ rollback เมื่อทำได้อย่างปลอดภัย

## End Maintenance Mode
1. Read current state
2. Remove only managed/approved Internet default route for DB Server
3. Preserve local subnet route and NIC
4. Verify DB Server remains reachable on LAN
5. Verify SQL TCP/connectivity
6. Verify Internet is unavailable according to Normal Mode policy
7. Record audit result

## Windows Update Procedure
- Enter Maintenance Mode
- Run approved Windows Update process
- Reboot if required
- After reboot verify SQL service and network state
- End Maintenance Mode
- Run diagnostics and capture evidence

## Remote Support Procedure
- Enter Maintenance Mode
- Start/use AnyDesk according to local policy
- Perform repair
- Run diagnostics
- Terminate remote session/software state as appropriate
- End Maintenance Mode
- Verify Normal Mode

## Failure Handling
หาก remote session หลุดระหว่าง network change:
- Do not blindly re-run destructive commands
- Inspect actual state locally/onsite
- Use Engine diagnostics/read-state first
- Apply desired-state operation only after validation

## Configuration Change
การเปลี่ยน IP/subnet/gateway/SQL port/client allow-list ต้อง:
1. Update SSOT docs/config design
2. Review impact
3. Implement
4. Test
5. Attach evidence
