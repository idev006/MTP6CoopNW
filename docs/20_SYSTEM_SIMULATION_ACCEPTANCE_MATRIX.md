# 20 — System Simulation & Acceptance Matrix

- Status: ACTIVE
- Owner: Engineering Team
- Purpose: กำหนดสถานการณ์ทดสอบที่ระบบต้องรองรับก่อนเข้าสู่ destructive enforcement และ production rollout

## 1. Test Principles
1. Fake-first and sandbox-first.
2. No destructive Windows/network change in ordinary CI.
3. Every state-changing capability requires plan, apply, verify and rollback evidence.
4. No result is accepted as success without read-back verification.
5. Timeouts, retries and reconnect loops must be bounded.
6. Every critical scenario must produce structured audit evidence.

## 2. Site Baseline
- 1 DB Server
- 5 Clients
- Router/Gateway baseline: 192.168.1.1
- DB Server baseline: 192.168.1.10
- Client baseline: 192.168.1.101–192.168.1.105
- SQL TCP baseline: 1433
- All addresses remain design assumptions until onsite verification.

## 3. Scenario Families

### A — Normal Operations
- Core cold start
- Agent cold start
- staggered Agent startup
- clean Core restart
- clean Agent restart
- Windows reboot recovery
- all six hosts visible centrally
- healthy telemetry and policy revision consistency

### B — Connectivity and Network Faults
- Agent cannot reach Core
- Core temporarily unavailable
- one client disconnected
- DB Server link unavailable
- router unavailable
- switch/uplink interruption
- intermittent packet loss
- reconnect burst after Core recovery
- duplicate heartbeat
- stale/out-of-order heartbeat
- Agent clock skew
- slow transport and bounded retry

### C — SQL and Service Faults
- SQL service stopped
- SQL TCP unavailable
- host reachable but SQL unavailable
- wrong SQL port configuration
- SQL recovery
- required service stopped/restarted
- maintenance operation must preserve LAN/SQL reachability

### D — Policy and Scheduler
- first policy revision
- duplicate same revision/content
- same revision with conflicting content
- stale revision
- newer revision
- restart with last-known-valid policy
- exact start/end boundary
- midnight crossover
- weekday transition
- overlapping rules
- manual override priority
- maintenance priority
- emergency/safety priority

### E — Safety and Operation Lifecycle
- validation failure
- dry run / plan only
- approval timeout
- apply timeout
- partial apply failure
- verification failure
- rollback success
- rollback failure
- duplicate operation ID
- idempotent retry
- cancellation when allowed
- cancellation rejected when unsafe
- self-lockout prevention
- preserve control channel

### F — Security Boundary
- unsupported Agent role
- host identity mismatch
- unauthenticated/invalid transport identity
- wrong target
- stale/replayed message
- expired command
- unsupported schema
- malformed payload
- log secret redaction
- no arbitrary PowerShell command path
- SQL never exposed directly to WAN

### G — Operator and Support
- overview all hosts
- host detail
- stale/offline indication
- unknown-health indication
- alarm history
- policy preview
- maintenance enter/exit
- diagnostics bundle
- correlation-ID audit lookup
- recovery after operator error

### H — Reliability and Capacity
- six hosts heartbeat every 2–5 seconds
- reconnect storm after Core restart
- long-running soak
- log growth
- Core persistence restart
- Agent cache restart
- slow adapter
- adapter timeout
- bounded queue/backoff
- no infinite wait

## 4. M6.1 Sandbox Evidence
Current M6.1 sandbox checks cover:
- six-host central monitoring
- ONLINE → STALE → OFFLINE boundaries
- site-wide outage convergence
- degraded heartbeat reporting
- Core receipt-time freshness
- role validation
- replay/stale heartbeat rejection
- duplicate heartbeat idempotency
- conflicting same-timestamp heartbeat rejection
- never-seen host alarm
- unknown-health alarm

## 5. Gate Policy
M9 destructive enforcement remains blocked until:
1. M6.1 non-destructive gates are green.
2. M7 policy/version/replay tests are green.
3. M8 plan/timeout/verify/rollback tests are green.
4. authenticated Agent identity binding is implemented for the real transport.
5. site network baseline is verified.
6. self-lockout and control-channel preservation tests pass in a controlled Windows environment.
