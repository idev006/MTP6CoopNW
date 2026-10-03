# PowerShell Adapter Layer

PowerShell is the Windows enforcement/inspection adapter layer for MTP6CoopNW.

## M0 Rule
The bootstrap phase contains no destructive Windows operations.

Future modules:
- MTP6.Network
- MTP6.Firewall
- MTP6.Services
- MTP6.Sql

Rules:
- no business policy in PowerShell
- structured objects/results only
- no UI rendering
- no arbitrary remote shell capability
- destructive operations require plan/apply/verify/rollback contracts
