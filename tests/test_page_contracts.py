from dataclasses import replace

import pytest

from saucedemo.app import Shop
from saucedemo.rules import calculate_totals

pytestmark = pytest.mark.component


@pytest.fixture
def local_shop(browser, settings):
    context = browser.new_context(viewport=settings.viewport)
    try:
        page = context.new_page()
        page.set_default_timeout(500)
        yield Shop(page, replace(settings, timeout_ms=300))
    finally:
        context.close()


@pytest.mark.parametrize("wrong", ["29.990", "129.99", "29.991"])
def test_money_rejects_partial_match(local_shop, wrong, monkeypatch):
    overview = local_shop.overview
    monkeypatch.setattr(overview, "assert_url", lambda: None)
    overview.page.set_content(
        f'<div data-test="subtotal-label">Item total: ${wrong}</div><div data-test="tax-label">Tax: $2.40</div><div data-test="total-label">Total: $32.39</div>'
    )
    with pytest.raises(AssertionError):
        overview.assert_totals(calculate_totals("29.99", "0.08"))


def test_money_accepts_exact_values(local_shop, monkeypatch):
    overview = local_shop.overview
    monkeypatch.setattr(overview, "assert_url", lambda: None)
    overview.page.set_content(
        '<div data-test="subtotal-label">Item total: $29.99</div><div data-test="tax-label">Tax: $2.40</div><div data-test="total-label">Total: $32.39</div>'
    )
    overview.assert_totals(calculate_totals("29.99", "0.08"))


def test_inventory_waits_for_expected_count(local_shop, monkeypatch):
    inventory = local_shop.inventory
    monkeypatch.setattr(inventory, "assert_loaded", lambda: None)
    inventory.page.set_content('<div class="inventory_item_name">Only product</div>')
    with pytest.raises(AssertionError):
        inventory.product_names(2)
    assert inventory.product_names(1) == ["Only product"]


def test_loaded_inventory_not_coupled_to_six_products(local_shop, monkeypatch):
    inventory = local_shop.inventory
    monkeypatch.setattr(inventory, "assert_url", lambda: None)
    inventory.page.set_content('<select data-test="product-sort-container"></select>')
    inventory.assert_loaded()
