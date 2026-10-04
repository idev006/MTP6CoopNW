from __future__ import annotations

import json
from pathlib import Path

import pytest

pytestmark = pytest.mark.contract

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "docs" / "use_case_catalog.json"
EVIDENCE = ROOT / "docs" / "use_case_evidence.json"


def test_all_72_use_cases_have_sandbox_completion_evidence() -> None:
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))

    expected = {
        use_case_id
        for ids in catalog["domains"].values()
        for use_case_id in ids
    }
    actual = set(evidence["useCases"])

    assert len(expected) == 72
    assert actual == expected
    assert evidence["sandboxCompletion"] == {"completed": 72, "total": 72}
    assert all(
        item["sandboxStatus"] == "COMPLETE"
        for item in evidence["useCases"].values()
    )


def test_every_use_case_has_at_least_one_automated_evidence_path() -> None:
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))

    for use_case_id, item in evidence["useCases"].items():
        assert item["evidence"], use_case_id
        assert all(path.startswith("tests/") for path in item["evidence"])
