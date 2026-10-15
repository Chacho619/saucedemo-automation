from playwright.sync_api import expect

from saucedemo.settings import Settings


class BasePage:
    path = "/"

    def __init__(self, page, settings=None):
        self.page = page
        self.settings = settings or Settings.from_env()
        self.base_url = self.settings.base_url

    def open(self, path=None):
        self.page.goto(self.base_url + (self.path if path is None else path))

    def assert_url(self):
        expect(self.page).to_have_url(self.base_url + self.path)

    def reload(self):
        self.page.reload()

    def assert_error(self, message):
        expect(self.page.locator('[data-test="error"]')).to_contain_text(message)
