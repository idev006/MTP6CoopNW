# 13 — Team Operating Model & RACI

## 1. Core Roles

### Senior Software Engineer (SSE)
Owns:
- Core architecture
- Python implementation
- Contracts/schemas
- Agent lifecycle
- API/transport abstractions
- automated tests
- packaging/versioning

### Senior Network Engineer (SNE)
Owns:
- topology
- IP/subnet/gateway
- firewall/network enforcement design
- connectivity and recovery
- network safety review
- port policy semantics

### Senior Process Engineer (SPE)
Owns:
- process flow
- state model
- schedule logic requirements
- interlocks
- alarm taxonomy
- operator workflow
- recovery sequence
- operational KPI

### Operations / System Administrator (OPS)
Owns:
- site verification
- installation
- approved policy operation
- incident evidence
- operational acceptance

### Project Owner / Management (PO)
Owns:
- policy intent
- scope priorities
- acceptance of business/operational requirements
- approval of high-impact change

## 2. RACI

| Work Item | PO | SSE | SNE | SPE | OPS |
|---|---|---|---|---|---|
| Project goals/scope | A | C | C | R | C |
| Functional requirements | A | R | C | R | C |
| Core architecture | C | A/R | C | C | I |
| Network topology | I | C | A/R | C | C |
| State/process design | C | C | C | A/R | C |
| Adapter contracts | I | A/R | R | C | C |
| Firewall policy implementation | I | C | A/R | C | C |
| Schedule semantics | C | R | C | A/R | C |
| UI workflow | C | R | C | A/R | C |
| Security review | I | R | A/R | C | C |
| Test strategy | I | A/R | R | R | C |
| Site acceptance | A | C | C | C | R |
| Production rollout | I | C | R | C | A/R |
| Incident recovery | I | C | A/R | R | R |
| ADR approval | C | A/R | C | C | I |

R = Responsible, A = Accountable, C = Consulted, I = Informed

## 3. Collaboration Rules
1. Requirement change begins in SSOT
2. No architecture decision lives only in chat or code
3. Network change requires SNE review
4. State/interlock/alarm change requires SPE review
5. Core/contract change requires SSE review
6. Production rollout requires OPS verification
7. High-impact policy change requires PO approval
8. Evidence accompanies acceptance

## 4. Handoff Checklist

### Requirement → Design
- requirement ID
- actor/use case
- desired outcome
- constraints
- failure behavior
- security impact

### Design → Implementation
- contract/schema
- state transition
- adapter ownership
- error categories
- test cases
- rollback expectation

### Implementation → Test
- version/commit
- test environment
- known limitations
- migration/config change
- expected evidence

### Test → Operations
- installation package
- config template
- runbook
- rollback
- health check
- acceptance checklist

## 5. Communication Artifact Priority
1. SSOT documents
2. ADR
3. Versioned contracts/schemas
4. Test evidence
5. Issues/PR discussions
6. Chat/conversation

If sources conflict, higher item in this list prevails unless formally superseded.
