from playwright.sync_api import expect

from .base import BasePage


class InventoryPage(BasePage):
    path = "/inventory.html"

    def assert_loaded(self):
        self.assert_url()
        expect(self.page.locator('[data-test="product-sort-container"]')).to_be_visible()

    def add(self, name):
        row = self.page.locator(".inventory_item").filter(
            has=self.page.locator(".inventory_item_name").get_by_text(name, exact=True)
        )
        row.get_by_role("button", name="Add to cart", exact=True).click()

    def open_product(self, name):
        self.page.locator(".inventory_item_name").get_by_text(name, exact=True).click()

    def sort(self, option):
        self.page.locator('[data-test="product-sort-container"]').select_option(option)

    def product_names(self, expected_count):
        self.assert_loaded()
        expect(self.page.locator(".inventory_item_name")).to_have_count(
            expected_count, timeout=self.settings.timeout_ms
        )
        return self.page.locator(".inventory_item_name").all_text_contents()

    def assert_added_count(self, count):
        expect(self.page.get_by_role("button", name="Remove", exact=True)).to_have_count(count)

    def assert_product_names(self, names):
        self.assert_loaded()
        expect(self.page.locator(".inventory_item_name")).to_have_text(names)

    def assert_prices(self, prices):
        self.assert_loaded()
        expect(self.page.locator(".inventory_item_price")).to_have_text([f"${price:.2f}" for price in prices])
