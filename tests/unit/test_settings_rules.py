import json
from decimal import Decimal

import pytest

from saucedemo.rules import calculate_totals, load_catalog
from saucedemo.settings import Settings

pytestmark = pytest.mark.unit


@pytest.fixture(autouse=True)
def clean_environment(monkeypatch):
    for name in [
        "BASE_URL",
        "BROWSER",
        "HEADED",
        "VIEWPORT",
        "TIMEOUT_MS",
        "NAVIGATION_TIMEOUT_MS",
        "CAPTURE_EVIDENCE",
        "CATALOG_PATH",
    ]:
        monkeypatch.delenv(name, raising=False)


@pytest.mark.parametrize(
    "name,value",
    [
        ("BASE_URL", "ftp://example.com"),
        ("BASE_URL", "https://user:password@example.com"),
        ("BASE_URL", "https://example.com?token=x"),
        ("BROWSER", "unknown"),
        ("VIEWPORT", "0x900"),
        ("VIEWPORT", "mobile"),
        ("TIMEOUT_MS", "-1"),
        ("NAVIGATION_TIMEOUT_MS", "abc"),
        ("HEADED", "maybe"),
        ("CAPTURE_EVIDENCE", "yes"),
    ],
)
def test_invalid_settings(monkeypatch, name, value):
    monkeypatch.setenv(name, value)
    with pytest.raises(ValueError):
        Settings.from_env()


def test_cli_overrides_environment(monkeypatch):
    monkeypatch.setenv("BROWSER", "firefox")
    monkeypatch.setenv("VIEWPORT", "800x600")
    settings = Settings.from_env(browser="webkit", viewport="390x844", headed=True)
    assert settings.browser == "webkit"
    assert settings.viewport == {"width": 390, "height": 844}
    assert settings.headed
    assert not settings.evidence


@pytest.mark.parametrize(
    "subtotal,rate,tax,total",
    [
        ("29.99", "0.08", "2.40", "32.39"),
        ("0", "0.08", "0.00", "0.00"),
        ("0.05", "0.10", "0.01", "0.06"),
        ("113.94", "0.08", "9.12", "123.06"),
    ],
)
def test_totals_rounding(subtotal, rate, tax, total):
    result = calculate_totals(subtotal, rate)
    assert result.tax == Decimal(tax)
    assert result.total == Decimal(total)


@pytest.mark.parametrize("subtotal,rate", [("-1", ".08"), ("1", "1.1"), ("NaN", ".08")])
def test_invalid_totals(subtotal, rate):
    with pytest.raises(ValueError):
        calculate_totals(subtotal, rate)


def test_catalog_can_change_without_changing_pages(tmp_path):
    path = tmp_path / "catalog.json"
    path.write_text(json.dumps({"products": {"New Product": "12.34"}, "tax_rate": "0.12"}))
    products, rate = load_catalog(path)
    assert products == {"New Product": Decimal("12.34")}
    assert rate == Decimal("0.12")


@pytest.mark.parametrize(
    "data",
    [
        {"products": {}, "tax_rate": "0.08"},
        {"products": {"Product": "-1"}, "tax_rate": "0.08"},
        {"products": {"Product": "NaN"}, "tax_rate": "0.08"},
        {"products": {"Product": "1.001"}, "tax_rate": "0.08"},
    ],
)
def test_invalid_catalog(tmp_path, data):
    path = tmp_path / "catalog.json"
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError):
        load_catalog(path)
