from playwright.sync_api import expect

from .base import BasePage


class CartPage(BasePage):
    path = "/cart.html"

    def assert_count(self, count):
        expect(self.page.locator(".cart_item")).to_have_count(count)

    def assert_product(self, name):
        expect(self.page.locator(".inventory_item_name")).to_have_text(name)

    def remove(self, name):
        row = self.page.locator(".cart_item").filter(
            has=self.page.locator(".inventory_item_name").get_by_text(name, exact=True)
        )
        row.get_by_role("button", name="Remove", exact=True).click()

    def continue_shopping(self):
        self.page.get_by_role("button", name="Continue Shopping", exact=True).click()

    def checkout(self):
        self.page.locator('[data-test="checkout"]').click()
