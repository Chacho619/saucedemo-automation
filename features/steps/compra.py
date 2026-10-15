from decimal import Decimal

from behave import given, then, when

from saucedemo.config import login_profile
from saucedemo.data import PRODUCTS, TAX_RATE
from saucedemo.rules import calculate_totals


@given("que inicié sesión como usuario estándar")
def login(context):
    context.shop.login_page.login()
    context.shop.inventory.assert_loaded()


@when('agrego "{name}" al carrito')
def add(context, name):
    context.shop.inventory.add(name)
    context.products.append(name)


@when("completo mis datos de checkout")
def checkout(context):
    context.shop.header.open_cart()
    context.shop.cart.checkout()
    context.shop.information.submit()


@then("el resumen tiene importes correctos")
def totals(context):
    context.shop.overview.assert_products(context.products)
    context.shop.overview.assert_totals(
        calculate_totals(sum((PRODUCTS[n] for n in context.products), Decimal("0")), TAX_RATE)
    )


@when("finalizo la compra")
def finish(context):
    context.shop.overview.finish()


@then("veo la confirmación de compra")
def confirmation(context):
    context.shop.complete.assert_confirmation()


@when('intento entrar con el perfil "{profile}"')
def invalid_login(context, profile):
    login_profile(context.shop.login_page, profile)


@then('veo el error "{message}"')
def error(context, message):
    context.shop.login_page.assert_error(message)
