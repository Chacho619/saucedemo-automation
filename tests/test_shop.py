from decimal import Decimal

import pytest

from saucedemo.config import login_profile
from saucedemo.data import PRODUCTS, TAX_RATE
from saucedemo.rules import calculate_totals

pytestmark = pytest.mark.e2e


@pytest.mark.smoke
def test_LOG_02_login(shop):
    shop.login_page.login()
    shop.inventory.assert_loaded()


@pytest.mark.parametrize(
    "profile,message",
    [
        ("locked", "Sorry, this user has been locked out."),
        ("empty", "Username is required"),
        ("missing_password", "Password is required"),
        ("missing_user", "Username is required"),
        ("unknown_user", "Username and password do not match"),
        ("wrong_password", "Username and password do not match"),
        ("both_wrong", "Username and password do not match"),
    ],
    ids=[
        "locked",
        "empty",
        "missing-password",
        "missing-user",
        "unknown-user",
        "wrong-password",
        "both-wrong",
    ],
)
def test_LOG_03_to_09_invalid_login(shop, profile, message):
    login_profile(shop.login_page, profile)
    shop.login_page.assert_error(message)
    shop.login_page.assert_url()


@pytest.mark.parametrize(
    "path", ["/inventory.html", "/cart.html", "/checkout-step-one.html", "/checkout-step-two.html"]
)
def test_SES_01_to_03_protected_routes(shop, path):
    shop.login_page.open(path)
    shop.login_page.assert_loaded()
    shop.login_page.assert_url()


def test_SES_04_to_06_logout(shop):
    shop.login_page.login()
    shop.header.logout()
    shop.login_page.assert_loaded()
    shop.inventory.open()
    shop.login_page.assert_loaded()


@pytest.mark.parametrize(
    "sort,descending,by_price",
    [
        ("az", False, False),
        ("za", True, False),
        ("lohi", False, True),
        ("hilo", True, True),
    ],
)
def test_CAT_05_to_08_sort(shop, sort, descending, by_price):
    shop.login_page.login()
    shop.inventory.sort(sort)
    expected_names = sorted(PRODUCTS, key=(lambda n: PRODUCTS[n]) if by_price else None, reverse=descending)
    if by_price:
        shop.inventory.assert_prices(sorted(PRODUCTS.values(), reverse=descending))
    else:
        shop.inventory.assert_product_names(expected_names)
    names = shop.inventory.product_names(len(PRODUCTS))
    assert sorted(names) == sorted(PRODUCTS)
    values = [PRODUCTS[n] if by_price else n for n in names]
    assert values == sorted(values, reverse=descending)


@pytest.mark.parametrize("name,price", PRODUCTS.items())
def test_CAT_02_DET_01_to_07_product(shop, name, price):
    shop.login_page.login()
    shop.inventory.add(name)
    shop.inventory.open_product(name)
    shop.details.assert_product(name, price)
    shop.details.remove()
    shop.header.assert_cart_count(0)
    shop.details.add()
    shop.header.open_cart()
    shop.cart.assert_count(1)
    shop.cart.assert_product(name)


def test_CAR_01_to_08_all_products_and_remove(shop):
    shop.login_page.login()
    for name in PRODUCTS:
        shop.inventory.add(name)
    shop.header.assert_cart_count(6)
    shop.header.open_cart()
    shop.cart.assert_count(6)
    for name in PRODUCTS:
        shop.cart.remove(name)
    shop.cart.assert_count(0)
    shop.header.assert_cart_count(0)


def test_CAR_12_14_persistence(shop):
    shop.login_page.login()
    shop.inventory.add("Sauce Labs Backpack")
    shop.header.open_cart()
    shop.cart.reload()
    shop.cart.assert_product("Sauce Labs Backpack")
    shop.cart.continue_shopping()
    shop.inventory.assert_loaded()
    shop.inventory.assert_added_count(1)


@pytest.mark.parametrize(
    "first,last,postal,error",
    [
        ("", "", "", "First Name is required"),
        ("", "Pérez", "01000", "First Name is required"),
        ("Ana", "", "01000", "Last Name is required"),
        ("Ana", "Pérez", "", "Postal Code is required"),
    ],
)
def test_INF_02_to_05_required(shop, first, last, postal, error):
    shop.login_page.login()
    shop.inventory.add("Sauce Labs Backpack")
    shop.header.open_cart()
    shop.cart.checkout()
    shop.information.submit(first, last, postal)
    shop.information.assert_error(error)
    shop.information.assert_url()


@pytest.mark.smoke
@pytest.mark.parametrize(
    "names", [["Sauce Labs Backpack"], ["Sauce Labs Onesie", "Sauce Labs Bike Light"], list(PRODUCTS)]
)
def test_FIN_01_to_13_purchase(shop, names):
    shop.login_page.login()
    for name in names:
        shop.inventory.add(name)
    shop.header.open_cart()
    shop.cart.checkout()
    shop.information.submit()
    shop.overview.assert_products(names)
    shop.overview.assert_totals(calculate_totals(sum((PRODUCTS[n] for n in names), Decimal("0")), TAX_RATE))
    shop.overview.finish()
    shop.complete.assert_confirmation()
    shop.header.assert_cart_count(0)
    shop.complete.back_to_products()
    shop.inventory.assert_loaded()
