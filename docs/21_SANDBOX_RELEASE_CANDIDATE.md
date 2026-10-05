# 21 — Sandbox Release Candidate

- Status: READY FOR CONTROLLED REAL-WORLD TESTING
- Date: 2026-10-04
- Scope: Engine/application behavior in isolated sandbox; no destructive Windows/network command executed.

## Completion model

The engineering/sandbox scope is considered complete when the following are present and verified:

1. Monitoring Core and Agent boundaries
2. Replaceable UI facade
3. Ports/Adapters and composition roots
4. Policy/Scheduler engine
5. Host State resolution
6. Operation Stage lifecycle
7. Planner / dry-run model
8. Apply / verify / rollback reference engine
9. Drift detection and reconciliation
10. Six-host pilot simulator
11. Automated acceptance checks
12. Operational documentation and safety gates

## Sandbox evidence

Executed in an isolated Python sandbox:

- 34 automated tests: PASS
- sandbox acceptance runner: 9/9 PASS
- deterministic random policy/reconciliation matrix: 5,000 PASS
- policy revision sequence/replay matrix: 5,000 PASS
- six-host 24-hour heartbeat soak at 3-second cadence: 172,800 heartbeats PASS
- Python compileall: PASS

## Critical scenarios verified

- exact schedule boundary
- overnight schedule
- deterministic policy priority
- equal-priority conflict rejection
- policy hash/revision/replay semantics
- stale revision rejection
- duplicate policy idempotency
- planner control-channel interlock
- safe managed-field planning only
- apply/read-back verification
- rollback after simulated failure
- bounded apply/verify timeout
- drift detection/reconciliation
- host-state priority
- DB maintenance Internet enable while preserving LAN/DB state
- 1 DB Server + 5 Clients ONLINE/STALE/OFFLINE convergence

## Safety boundary

The sandbox executor is a reference/fake enforcement engine. It does not mutate the local OS, NIC, route table, Windows Firewall or SQL Server. Real Windows/SQL enforcement remains subject to controlled integration testing on a dedicated test environment.

## Real-test entry criteria

Before enabling destructive capability on a real machine:

1. verify actual topology/IP/interface/SQL instance and port
2. use a dedicated Windows test host or VM first
3. confirm project-owned firewall rule prefix and rollback snapshot
4. verify control-channel/LAN reachability before and after each operation
5. start with plan/dry-run and read-back verification
6. test rollback before expanding scope
7. keep SQL closed to WAN
8. retain last-known-valid policy on Core outage
9. use authenticated transport identity before remote state-changing commands
10. record audit evidence for every test

## Project status

Engineering + sandbox validation: 100%.

Interpretation: the codebase is ready to enter controlled real-world integration/pilot testing. This is not a claim that production deployment has already been proven on the real site.
