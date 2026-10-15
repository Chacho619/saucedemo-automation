from saucedemo.components.header import HeaderComponent
from saucedemo.pages.cart import CartPage
from saucedemo.pages.checkout import CheckoutCompletePage, CheckoutInformationPage, CheckoutOverviewPage
from saucedemo.pages.details import ProductDetailsPage
from saucedemo.pages.inventory import InventoryPage
from saucedemo.pages.login import LoginPage
from saucedemo.settings import Settings


class Shop:
    """Contenedor de Page Objects para un único contexto; no contiene selectores."""

    def __init__(self, page, settings=None):
        settings = settings or Settings.from_env()
        self.login_page = LoginPage(page, settings)
        self.inventory = InventoryPage(page, settings)
        self.details = ProductDetailsPage(page, settings)
        self.cart = CartPage(page, settings)
        self.information = CheckoutInformationPage(page, settings)
        self.overview = CheckoutOverviewPage(page, settings)
        self.complete = CheckoutCompletePage(page, settings)
        self.header = HeaderComponent(page)
