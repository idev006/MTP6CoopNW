# 14 — Scope & Change Control

## 1. Purpose
ป้องกัน scope creep และป้องกันการแก้ระบบตามคำขอเฉพาะหน้าโดยไม่มีผลกระทบ/หลักฐาน

## 2. Change Classes

### Class A — Configuration Change
Examples:
- add client
- adjust schedule
- change allowed port
- change Internet/DB policy

Expected:
- no architecture change
- policy/config revision
- validation + evidence

### Class B — Module/Adapter Change
Examples:
- new remote support adapter
- new notification channel
- new firewall mechanism

Expected:
- contract compatibility review
- integration tests
- ADR if boundary/semantics change

### Class C — Architecture Change
Examples:
- remove local agents
- move Core to cloud
- change trust boundary
- change policy priority model
- replace Python Core with another runtime

Expected:
- requirement update
- impact analysis
- ADR
- security review
- full regression/acceptance tests

### Class D — Emergency Change
Allowed only for incident containment.
Requirements:
- identify operator/reason/time
- preserve recovery path
- capture before/after
- follow-up SSOT reconciliation

## 3. Change Workflow
Request → Classify → Impact → Approve → Update SSOT → Implement → Test → Deploy → Verify → Evidence → Close

## 4. Mandatory Impact Questions
- Does this change affect DB availability?
- Does it risk losing control channel?
- Does it change Internet exposure?
- Does it affect SQL exposure?
- Does it alter policy priority?
- Does it alter schedule behavior?
- Does it require new firewall ports?
- Can it be rolled back?
- Does it require endpoint restart?
- Does it change secrets/credentials?
- Does UI need change?
- Does Agent need change?

## 5. Scope Guardrails
The following may not be added informally:
- business-data editing
- public SQL access
- arbitrary remote command shell
- uncontrolled PowerShell execution
- disabling security tools
- unmanaged firewall deletion
- credential storage in repository

## 6. Acceptance Rule
A change is not complete until:
- SSOT matches behavior
- tests pass
- actual state verified
- audit/evidence captured
- operational documentation updated when needed
