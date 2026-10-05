# 27 — Desktop UI/UX Design — PySide6

- Status: IMPLEMENTATION BASELINE v2
- Date: 2026-10-04
- UI Technology: Python + PySide6 (Qt 6)
- Architecture: UI is a replaceable mask over Facades / Presenter / ViewModel

Concrete Qt code renders ViewModels, collects operator intent, and invokes presentation Facades. Qt modules must not import Core, Engines, Adapters, persistence, PowerShell, SQL, network implementations, or the Composition Root.

Primary navigation:
1. Overview
2. Hosts
3. Policies & Schedule
4. Alarms
5. Audit & History
6. System

The current UI baseline includes the complete six-page shell, Overview operational dashboard, Hosts inventory/search, Policies & Schedule layout boundary, Alarms summary, Audit contract placeholder, System synchronization metrics, event-driven updates, and architecture-boundary tests.

PySide6 is the reference Qt 6 binding. Qt-specific types remain inside presentation/qt so another UI technology can replace it without changing Engines.
