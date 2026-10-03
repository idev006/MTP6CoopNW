# 12 — Workflows, Pipelines & Diagrams

> Mermaid diagrams in this file are normative architectural communication aids. If implementation differs materially, update SSOT/ADR first.

## 1. System Context

```mermaid
flowchart LR
    Admin[Administrator / Operator] --> UI[Dashboard / CLI / API]
    UI --> Core[Central Control Core]
    Core <--> Agent1[Agent - Client 1]
    Core <--> Agent2[Agent - Client 2]
    Core <--> AgentN[Agent - Client N]
    Core <--> DBAgent[Agent - DB Server]
    Agent1 --> Win1[Windows / Firewall]
    Agent2 --> Win2[Windows / Firewall]
    AgentN --> WinN[Windows / Firewall]
    DBAgent --> DBWin[Windows / Firewall / SQL Server]
    DBWin --> SQL[(SQL Database)]
    Win1 --> Internet[(Internet)]
    Win2 --> Internet
    DBWin -. Maintenance only .-> Internet
```

## 2. Component Diagram

```mermaid
flowchart TB
    subgraph UI["Replaceable UI Layer"]
      Web[Web Dashboard]
      Desktop[Desktop UI]
      CLI[CLI / PowerShell UI]
    end

    subgraph Core["Python Control Core"]
      API[Application API]
      Policy[Policy Engine]
      State[State Engine]
      Scheduler[Scheduler]
      Alarm[Alarm Engine]
      Audit[Audit Engine]
      Registry[Host/Module Registry]
      Telemetry[Telemetry Aggregator]
    end

    subgraph Agent["Python Local Agent"]
      AgentCore[Agent Engine]
      LocalScheduler[Local Schedule Evaluator]
      Reconcile[Reconciliation]
      LocalCache[Last-known Policy Cache]
    end

    subgraph PS["PowerShell / Windows Adapter Layer"]
      Net[Network Adapter]
      FW[Firewall Adapter]
      Service[Service Adapter]
      SQLA[SQL Connectivity Adapter]
    end

    Web --> API
    Desktop --> API
    CLI --> API
    API --> Policy
    API --> State
    Policy --> Scheduler
    State --> Alarm
    API --> Registry
    Telemetry --> State
    State --> Audit
    Core <--> AgentCore
    AgentCore --> LocalScheduler
    AgentCore --> Reconcile
    AgentCore --> LocalCache
    Reconcile --> Net
    Reconcile --> FW
    Reconcile --> Service
    Reconcile --> SQLA
```

## 3. Policy Change Pipeline

```mermaid
flowchart LR
    Request[Policy Request] --> Validate[Validate Requirement]
    Validate --> Impact[Impact Analysis]
    Impact --> Docs[Update SSOT / ADR if needed]
    Docs --> PolicyRev[Create Policy Revision]
    PolicyRev --> Stage[Stage / Test]
    Stage --> Deploy[Distribute to Agents]
    Deploy --> Verify[Verify Desired vs Actual]
    Verify --> Evidence[Record Evidence / Audit]
    Verify -->|Fail| Rollback[Rollback / Recovery]
    Rollback --> Evidence
```

## 4. Software Delivery Pipeline

```mermaid
flowchart LR
    Req[SSOT Requirement] --> Design[Contract / ADR / Design]
    Design --> Code[Core / Module / Adapter Code]
    Code --> Unit[Unit Tests]
    Unit --> Integration[Windows Integration Tests]
    Integration --> Acceptance[Acceptance Tests]
    Acceptance --> Package[Versioned Package]
    Package --> Pilot[Pilot Host]
    Pilot --> Rollout[Controlled Rollout]
    Rollout --> Evidence[Production Evidence]
```

## 5. Sequence — Set Internet Access

```mermaid
sequenceDiagram
    actor O as Operator
    participant UI as Dashboard
    participant C as Control Core
    participant P as Policy Engine
    participant A as Local Agent
    participant F as Firewall/Network Adapter
    participant W as Windows

    O->>UI: Set Internet = BLOCK
    UI->>C: Command(host, policy)
    C->>C: Authorize + validate
    C->>P: Create new policy revision
    P-->>C: Effective desired state
    C->>A: ApplyPolicy(revision)
    A->>A: Validate + interlock
    A->>F: Enforce Internet policy
    F->>W: Apply managed rules/routes
    W-->>F: Result
    F-->>A: Structured result
    A->>A: Verify LAN + Internet state
    A-->>C: Command result + state event
    C->>C: Audit + update state
    C-->>UI: Confirm / alarm
    UI-->>O: Effective state shown
```

## 6. Sequence — Scheduled Access Transition

```mermaid
sequenceDiagram
    participant T as Time Adapter
    participant S as Local Scheduler
    participant A as Agent
    participant P as Cached Policy
    participant F as Enforcement Adapters
    participant C as Control Core

    T-->>S: Schedule boundary reached
    S->>P: Resolve effective policy
    P-->>S: BLOCKED desired state
    S->>A: Transition request
    A->>A: Interlock + plan
    A->>F: Enforce host/internet/db/ports
    F-->>A: Result
    A->>A: Read-back verification
    A-->>C: State event + audit payload
    C-->>A: Ack
```

## 7. Sequence — Agent Reconnect

```mermaid
sequenceDiagram
    participant A as Agent
    participant L as Local Policy Cache
    participant C as Control Core
    participant P as Policy Registry

    A->>L: Load last-known valid policy
    A->>A: Enforce/reconcile locally
    A->>C: Register + heartbeat(policyRevision)
    C->>P: Get latest policy revision
    P-->>C: Latest revision
    alt Agent stale
      C->>A: Push newer policy
      A->>A: Validate + apply + verify
      A-->>C: Applied revision + state
    else Agent current
      C-->>A: Continue
    end
```

## 8. State Diagram — Host Access

```mermaid
stateDiagram-v2
    [*] --> UNKNOWN
    UNKNOWN --> NORMAL: agent healthy + policy resolved
    NORMAL --> SCHEDULE_BLOCKED: schedule denies
    SCHEDULE_BLOCKED --> NORMAL: schedule allows
    NORMAL --> DISABLED: admin disable
    SCHEDULE_BLOCKED --> DISABLED: admin disable
    DISABLED --> NORMAL: authorized enable + schedule allows
    DISABLED --> SCHEDULE_BLOCKED: authorized enable + schedule denies
    NORMAL --> WARNING: drift/noncritical issue
    WARNING --> NORMAL: reconciled
    NORMAL --> FAULT: critical enforcement failure
    WARNING --> FAULT: escalation
    FAULT --> RECOVERY: recovery action
    RECOVERY --> NORMAL: verification pass
    RECOVERY --> FAULT: verification fail
    NORMAL --> OFFLINE: heartbeat timeout
    SCHEDULE_BLOCKED --> OFFLINE: heartbeat timeout
    DISABLED --> OFFLINE: heartbeat timeout
    OFFLINE --> UNKNOWN: heartbeat returns
```

## 9. State Diagram — DB Server

```mermaid
stateDiagram-v2
    [*] --> SERVER_NORMAL
    SERVER_NORMAL --> SERVER_MAINTENANCE: approved maintenance + interlocks pass
    SERVER_MAINTENANCE --> SERVER_NORMAL: end maintenance + verify Internet blocked
    SERVER_NORMAL --> FAULT: SQL/LAN/security failure
    SERVER_MAINTENANCE --> FAULT: verification failure
    FAULT --> RECOVERY
    RECOVERY --> SERVER_NORMAL: safe state restored
    RECOVERY --> FAULT: restore failed
```

## 10. Activity — Reconciliation Loop

```mermaid
flowchart TD
    Start([Timer/Event]) --> ReadDesired[Read Desired Policy]
    ReadDesired --> ReadActual[Read Actual Windows State]
    ReadActual --> Compare{Desired = Actual?}
    Compare -->|Yes| Publish[Publish Healthy Status]
    Compare -->|No| Safe{Safe to auto-converge?}
    Safe -->|Yes| Apply[Apply Managed Changes]
    Apply --> Verify{Verify?}
    Verify -->|Pass| Publish
    Verify -->|Fail| Alarm[Raise Fault / Recovery]
    Safe -->|No| Drift[Raise Drift Alarm]
    Drift --> Publish
    Alarm --> Publish
```

## 11. Deployment View

```mermaid
flowchart TB
    subgraph AdminPC["Management Host"]
      Dashboard[Dashboard]
      Core[Python Control Core]
      Audit[(Audit/State Store)]
    end

    subgraph C1["Client 1"]
      A1[Python Agent Service]
      P1[PowerShell Adapters]
    end

    subgraph C2["Client 2..N"]
      A2[Python Agent Service]
      P2[PowerShell Adapters]
    end

    subgraph DBS["Database Server"]
      AD[Python Agent Service]
      PD[PowerShell Adapters]
      SQL[(SQL Server)]
    end

    Dashboard --> Core
    Core --> Audit
    Core <--> A1
    Core <--> A2
    Core <--> AD
    A1 --> P1
    A2 --> P2
    AD --> PD
    PD --> SQL
```

## 12. Alarm Flow

```mermaid
flowchart LR
    Telemetry[Telemetry / Verification] --> Detect[Alarm Rule Evaluation]
    Detect --> Severity{Severity}
    Severity --> Info[INFO]
    Severity --> Warn[WARNING]
    Severity --> Fault[FAULT]
    Severity --> Critical[CRITICAL]
    Info --> Dashboard
    Warn --> Dashboard
    Fault --> Dashboard
    Critical --> Dashboard
    Fault --> Recovery[Recovery Workflow]
    Critical --> Recovery
    Dashboard --> Audit[Audit / Historian]
    Recovery --> Audit
```
