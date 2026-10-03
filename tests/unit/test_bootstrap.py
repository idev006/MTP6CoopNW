from __future__ import annotations

import pathlib
import tomllib

import mtp6coopnw


ROOT = pathlib.Path(__file__).resolve().parents[2]


def test_package_has_version() -> None:
    assert mtp6coopnw.__version__


def test_example_toml_files_are_valid() -> None:
    examples = sorted((ROOT / "config").glob("*.example.toml"))
    assert examples, "Expected at least one TOML example file."

    for path in examples:
        with path.open("rb") as file:
            parsed = tomllib.load(file)
        assert parsed["schema_version"] == 1, f"{path} must declare schema_version = 1"


def test_destructive_test_marker_is_not_default_behavior() -> None:
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert "destructive" in pyproject
