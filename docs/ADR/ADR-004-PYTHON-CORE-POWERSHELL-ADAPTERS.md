# ADR-004 — Python Control Core with PowerShell Windows Adapters

- Status: Accepted
- Date: 2026-10-03

## Context
MTP6CoopNW needs both rich control logic and deep Windows administration. Python is strong for policy/state/scheduler/API/telemetry/testing, while PowerShell is the native administration surface for Windows networking, firewall, services and related CIM cmdlets.

Using PowerShell for the entire platform would couple business/process logic to Windows scripting. Using Python alone would often recreate or wrap Windows administration APIs unnecessarily.

## Decision
1. Python is the primary language for:
   - Control Core
   - Policy Engine
   - State Engine
   - Scheduler
   - Alarm/Telemetry
   - Local Agent orchestration
   - API/transport abstraction
2. PowerShell is the primary Windows enforcement adapter for:
   - network
   - routes/gateway
   - firewall
   - Windows services
   - selected SQL/Windows operational checks
3. PowerShell modules return structured data and do not render UI
4. Python calls adapters through a single adapter boundary, not scattered subprocess calls
5. Adapter implementation may later move to CIM/native Windows API if the same contract is preserved/versioned

## Consequences
### Positive
- clean separation of control logic from Windows mechanics
- easier testing
- replaceable adapters
- better future UI/API portability
- native Windows operations remain understandable to administrators

### Trade-offs
- two-runtime packaging
- contract/serialization discipline required
- integration tests must cover Python ↔ PowerShell boundary

## Enforcement
Direct PowerShell command construction scattered across Python business logic is prohibited. Windows-specific operations must go through registered adapter interfaces.
