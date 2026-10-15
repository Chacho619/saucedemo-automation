from playwright.sync_api import expect


class HeaderComponent:
    def __init__(self, page):
        self.page = page

    def open_cart(self):
        self.page.locator(".shopping_cart_link").click()

    def assert_cart_count(self, count):
        badge = self.page.locator(".shopping_cart_badge")
        if count:
            expect(badge).to_have_text(str(count))
        else:
            expect(badge).to_have_count(0)

    def logout(self):
        self.page.get_by_role("button", name="Open Menu", exact=True).click()
        self.page.get_by_text("Logout", exact=True).click()
