from playwright.sync_api import expect

from saucedemo.config import required_env

from .base import BasePage


class LoginPage(BasePage):
    def login(self, user=None, password=None):
        user = required_env("SAUCE_USERNAME") if user is None else user
        password = required_env("SAUCE_PASSWORD") if password is None else password
        self.open()
        self.page.locator('[data-test="username"]').fill(user)
        self.page.locator('[data-test="password"]').fill(password)
        self.page.locator('[data-test="login-button"]').click()

    def assert_loaded(self):
        self.assert_url()
        expect(self.page.locator('[data-test="login-button"]')).to_be_visible()
