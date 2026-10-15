import os

import pytest
from playwright.sync_api import sync_playwright

from saucedemo.runtime import BrowserSession
from saucedemo.settings import Settings


def pytest_addoption(parser):
    parser.addoption("--headed", action="store_true", default=None)
    parser.addoption("--browser", choices=["chromium", "firefox", "webkit"], default=None)
    parser.addoption("--viewport", default=None, help="ANCHOxALTO")


@pytest.fixture(scope="session")
def settings(request):
    return Settings.from_env(
        browser=request.config.getoption("--browser"),
        headed=request.config.getoption("--headed"),
        viewport=request.config.getoption("--viewport"),
    )


@pytest.fixture(scope="session")
def browser(settings):
    with sync_playwright() as pw:
        instance = getattr(pw, settings.browser).launch(headless=not settings.headed)
        try:
            yield instance
        finally:
            instance.close()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    setattr(item, "rep_" + call.when, outcome.get_result())


@pytest.fixture
def shop(browser, settings, request):
    session = BrowserSession(browser, settings)
    try:
        yield session.start()
    finally:
        failed = any(
            getattr(request.node, "rep_" + stage, None) and getattr(request.node, "rep_" + stage).failed
            for stage in ("setup", "call")
        )
        session.close(
            failed=failed, identity=request.node.nodeid, worker=os.getenv("PYTEST_XDIST_WORKER", "main")
        )
