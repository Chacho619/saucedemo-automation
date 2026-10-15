from playwright.sync_api import sync_playwright

from saucedemo.runtime import BrowserSession
from saucedemo.settings import Settings


def before_all(context):
    context.settings = Settings.from_env()
    context.pw = sync_playwright().start()
    context.add_cleanup(context.pw.stop)
    context.browser = getattr(context.pw, context.settings.browser).launch(
        headless=not context.settings.headed
    )
    context.add_cleanup(context.browser.close)


def before_scenario(context, scenario):
    session = BrowserSession(context.browser, context.settings)
    # Cleanup registrado antes de start: funciona ante setup parcial y hooks fallidos.
    context.add_cleanup(
        lambda: session.close(
            failed=scenario.status.name in {"failed", "error", "hook_error"},
            runner="behave",
            identity=f"{scenario.filename}:{scenario.line}:{scenario.name}",
        )
    )
    context.shop = session.start()
    context.products = []
