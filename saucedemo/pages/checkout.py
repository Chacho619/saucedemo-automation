from playwright.sync_api import expect

from .base import BasePage


class CheckoutInformationPage(BasePage):
    path = "/checkout-step-one.html"

    def submit(self, first="Ana", last="Pérez", postal="01000"):
        self.page.locator('[data-test="firstName"]').fill(first)
        self.page.locator('[data-test="lastName"]').fill(last)
        self.page.locator('[data-test="postalCode"]').fill(postal)
        self.page.locator('[data-test="continue"]').click()


class CheckoutOverviewPage(BasePage):
    path = "/checkout-step-two.html"

    def assert_products(self, names):
        self.assert_url()
        expect(self.page.locator(".inventory_item_name")).to_have_text(names)

    def assert_totals(self, expected):
        self.assert_url()
        for selector, label, value in [
            ("subtotal-label", "Item total", expected.subtotal),
            ("tax-label", "Tax", expected.tax),
            ("total-label", "Total", expected.total),
        ]:
            expect(self.page.locator(f'[data-test="{selector}"]')).to_have_text(
                f"{label}: ${value:.2f}", timeout=self.settings.timeout_ms
            )

    def finish(self):
        self.page.locator('[data-test="finish"]').click()


class CheckoutCompletePage(BasePage):
    path = "/checkout-complete.html"

    def assert_confirmation(self):
        self.assert_url()
        expect(self.page.locator('[data-test="complete-header"]')).to_have_text("Thank you for your order!")

    def back_to_products(self):
        self.page.locator('[data-test="back-to-products"]').click()
