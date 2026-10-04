from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

pytestmark = pytest.mark.contract

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "docs" / "use_case_catalog.json"
MASTER = ROOT / "docs" / "23_MASTER_USE_CASE_CAPABILITY_MATRIX.md"
ID_PATTERN = re.compile(r"^UC-[A-Z]+-[0-9]{3}$")


def test_machine_readable_use_case_catalog_is_valid_and_unique() -> None:
    payload = json.loads(CATALOG.read_text(encoding="utf-8"))
    all_ids = [
        use_case_id
        for ids in payload["domains"].values()
        for use_case_id in ids
    ]

    assert payload["schemaVersion"] == 1
    assert len(all_ids) == len(set(all_ids))
    assert all(ID_PATTERN.fullmatch(use_case_id) for use_case_id in all_ids)
    assert len(all_ids) >= 60


def test_every_catalog_use_case_is_traceable_in_master_matrix() -> None:
    payload = json.loads(CATALOG.read_text(encoding="utf-8"))
    master = MASTER.read_text(encoding="utf-8")

    for ids in payload["domains"].values():
        for use_case_id in ids:
            assert use_case_id in master


def test_mandatory_control_domains_exist() -> None:
    payload = json.loads(CATALOG.read_text(encoding="utf-8"))
    required = {
        "HOST",
        "NETWORK",
        "SCHEDULE",
        "POLICY",
        "PLANNING",
        "OPERATIONS",
        "RECONCILIATION",
        "MONITORING",
        "UI",
        "AUDIT",
        "SECURITY",
        "RESILIENCE",
        "DATABASE",
    }

    assert required <= set(payload["domains"])
