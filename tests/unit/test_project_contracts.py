import ast
import csv
from pathlib import Path

import pytest
import yaml

pytestmark = pytest.mark.unit
ROOT = Path(__file__).resolve().parents[2]


def test_traceability_has_all_cases_and_real_test_references():
    with (ROOT / "docs/traceability.csv").open(encoding="utf-8-sig") as file:
        rows = list(csv.DictReader(file))
    assert len(rows) == 130
    assert len({row["caso"] for row in rows}) == 130
    known = {
        node.name
        for node in ast.walk(ast.parse((ROOT / "tests/test_shop.py").read_text(encoding="utf-8")))
        if isinstance(node, ast.FunctionDef)
    }
    for row in rows:
        assert row["estado"] in {
            "Automatizado",
            "Parcial",
            "Pendiente",
            "Manual pendiente",
            "Requiere requisito",
        }
        if row["prueba"]:
            assert row["prueba"].split("::")[1].split("[")[0] in known
        if row["estado"] in {"Automatizado", "Parcial"}:
            assert row["prueba"]


def test_ci_has_browser_viewport_matrix_and_restricted_reports():
    workflow = yaml.load(
        (ROOT / ".github/workflows/tests.yml").read_text(encoding="utf-8"), Loader=yaml.BaseLoader
    )
    assert "pull_request" in workflow["on"]
    assert workflow["permissions"] == {"contents": "read"}
    quality = workflow["jobs"]["quality"]
    assert any("playwright install --with-deps chromium" in step.get("run", "") for step in quality["steps"])
    assert any("pytest -m 'unit or component'" in step.get("run", "") for step in quality["steps"])
    e2e = workflow["jobs"]["e2e"]
    assert e2e["if"] == "github.event_name != 'pull_request'"
    matrix = e2e["strategy"]["matrix"]["include"]
    assert {entry["browser"] for entry in matrix} == {"chromium", "firefox", "webkit"}
    assert any(entry["viewport"] == "390x844" for entry in matrix)
    upload = e2e["steps"][-1]
    assert upload["with"]["path"] == "artifacts/**/*.xml"
    assert upload["with"]["retention-days"] == "7"
