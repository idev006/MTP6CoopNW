# ADR-007 — Agent-Initiated Mutual-TLS Core Transport

- Status: Accepted
- Date: 2026-10-04

## Context
MTP6CoopNW is moving from in-memory/fake transport toward a real Core↔Agent channel. The channel will eventually carry telemetry, policy revisions and approved control operations for Windows/network infrastructure. A generic unauthenticated REST endpoint or ad-hoc remote PowerShell path would create an unacceptable trust boundary.

Managed hosts are on the internal LAN, but the LAN is not implicitly trusted. The design should also avoid requiring inbound listeners on every client where practical.

## Decision
1. The production baseline transport is **agent-initiated HTTPS using mutual TLS (mTLS)**.
2. Each Agent receives a unique client certificate/identity. The Core validates the client certificate against the project trust chain and maps it to an approved `host_id`.
3. Agents validate the Core certificate and approved trust chain. Certificate validation must never be disabled in production.
4. Normal traffic direction is Agent → Core:
   - heartbeat / telemetry upload
   - policy/version polling or long-polling
   - command acknowledgement/result upload
5. No general-purpose remote shell, arbitrary PowerShell execution, or arbitrary command payload is exposed by the transport.
6. Application messages remain versioned structured contracts independent of HTTP implementation.
7. Every state-changing command must carry:
   - operation/command ID
   - correlation ID
   - target host
   - policy/config revision where applicable
   - issued/expiry time
   - authenticated issuer context
8. Agents reject expired, malformed, duplicate/replayed, wrong-target or unsupported command messages.
9. Certificate/private-key material is provisioned outside Git and never written to application logs.
10. Certificate rotation/revocation must be supported operationally before destructive enforcement is enabled.
11. Transport timeout, retry and reconnect behavior must be bounded and observable.
12. Core freshness is based on **Core receipt time**. Agent timestamps are retained for diagnostics and clock-skew detection, not as the authoritative freshness clock.

## Consequences

### Positive
- Strong machine identity at both ends.
- No shared bearer secret across all hosts.
- Reduces need for inbound client firewall exposure.
- Compatible with future REST, long-poll or WebSocket-style delivery behind the same application contracts.
- Better replay/audit boundary before destructive actions are introduced.

### Trade-offs
- Requires certificate provisioning and lifecycle operations.
- Local clock quality still matters for diagnostics, certificate validity and command expiry.
- Core availability and certificate rotation procedures must be documented and tested.

## Safety
Loss of Core connectivity does not remove the Agent's last-known valid policy. No destructive capability may rely on a bypass channel outside the authenticated contract.

## Implementation Gate
M7 may implement policy semantics with fake/in-process transport, but production policy distribution and all M8/M9 command paths must conform to this ADR before real enforcement is enabled.
