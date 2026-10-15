from playwright.sync_api import expect

from .base import BasePage


class ProductDetailsPage(BasePage):
    def assert_product(self, name, price):
        expect(self.page.locator(".inventory_details_name")).to_have_text(name)
        expect(self.page.locator(".inventory_details_price")).to_have_text(f"${price:.2f}")

    def add(self):
        self.page.get_by_role("button", name="Add to cart", exact=True).click()

    def remove(self):
        self.page.get_by_role("button", name="Remove", exact=True).click()
