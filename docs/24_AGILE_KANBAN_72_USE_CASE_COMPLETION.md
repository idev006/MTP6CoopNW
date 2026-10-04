# 24 — Agile Kanban: 72 Use Case Completion

- Date: 2026-10-04
- Goal: close engineering/sandbox coverage for all 72 use cases in the Master Matrix today.
- Production rule: real Windows/SQL/network acceptance remains a separate controlled gate.

## Working policy

WIP limit: 1 capability batch per engineering lane.  
Definition of Done: contract + implementation + automated evidence + failure path + observable/audit behavior where applicable.  
Push policy: local/sandbox first, one logical integration push after review.

## Kanban

### BACKLOG
None for engineering/sandbox scope after this batch.

### IN PROGRESS
None after completion review.

### REVIEW / TEST
- GitHub-hosted CI remains externally blocked when runner_id=0 and steps=[].
- Local isolated completion suite executed before integration.

### DONE
- Host control and per-host policy controls
- Internet/LAN/Database separation
- Per-host ports
- TCP/UDP protocol rules
- Inbound/outbound direction rules
- Destination restrictions
- SQL WAN safety guard
- Weekly schedules and overnight windows
- Holiday/special-date override
- Temporary access with automatic expiry
- Policy priority/revision/replay/conflict
- Last-known-valid recovery and safe-hold fallback
- Dry-run/planning/interlocks
- Bounded apply/verify/rollback
- Idempotent operation retries
- Drift/reconciliation
- Heartbeat/freshness/health monitoring
- SQL/firewall/network/service observability boundaries
- Alarm raise/acknowledge/clear lifecycle
- Snapshot + reactive UI event stream
- Event replay/resync
- Headless UI facade/presenter automation
- Actor-aware mutation audit
- Viewer/Operator/Admin authorization model
- Agent-initiated host identity/replay guard
- Least-privilege SQL credential validator
- Restart persistence primitive
- Six-host site simulation and outage convergence
- Replaceable UI/adapters/composition architecture

## Completion statement

Engineering/sandbox use-case coverage: 72/72.

This means every use case in the Master Matrix now has an implementation or executable contract and sandbox evidence path. Items that touch real Windows Firewall, routing, SQL Server, Windows Service lifecycle, certificates or site topology are READY FOR CONTROLLED REAL-WORLD INTEGRATION; they are not declared production-proven until that gate passes.
