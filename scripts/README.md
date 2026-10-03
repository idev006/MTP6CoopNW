# Scripts

Scripts in this directory support development, testing, packaging, and future deployment.

## M0
- scripts/test/run-tests.ps1 — local non-destructive test runner
- scripts/dev/validate-config.ps1 — validates example TOML syntax/schema version

## Safety
No M0 script may alter Windows Firewall, routes, IP addresses, or SQL configuration.
