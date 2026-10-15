import pytest


@pytest.fixture(autouse=True)
def isolated_framework_environment(monkeypatch):
    for key in [
        "BASE_URL",
        "BROWSER",
        "HEADED",
        "VIEWPORT",
        "TIMEOUT_MS",
        "NAVIGATION_TIMEOUT_MS",
        "CAPTURE_EVIDENCE",
        "ARTIFACTS_DIR",
        "CATALOG_PATH",
    ]:
        monkeypatch.delenv(key, raising=False)
