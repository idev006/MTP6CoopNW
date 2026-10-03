from __future__ import annotations

import pathlib

from mtp6coopnw.persistence import JsonFilePolicyStore


def test_policy_cache_survives_store_recreation(tmp_path: pathlib.Path) -> None:
    path = tmp_path / "policy-cache.json"
    first = JsonFilePolicyStore(path)
    first.save(
        "CLIENT-01",
        {"policy_revision": 9, "internet": {"allowed": False}},
    )

    second = JsonFilePolicyStore(path)
    loaded = second.get("CLIENT-01")

    assert loaded is not None
    assert loaded["policy_revision"] == 9
    assert loaded["internet"]["allowed"] is False


def test_policy_cache_returns_copy(tmp_path: pathlib.Path) -> None:
    store = JsonFilePolicyStore(tmp_path / "policy-cache.json")
    store.save("CLIENT-01", {"policy_revision": 2, "nested": {"enabled": True}})

    first = store.get("CLIENT-01")
    assert first is not None
    first["nested"]["enabled"] = False

    second = store.get("CLIENT-01")
    assert second is not None
    assert second["nested"]["enabled"] is True
