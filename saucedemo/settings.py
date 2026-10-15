"""Configuración validada compartida por ambos ejecutores."""

import os
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit
from uuid import uuid4


def positive_int(value, name):
    try:
        result = int(value)
    except (TypeError, ValueError) as error:
        raise ValueError(f"{name} debe ser un entero positivo") from error
    if result <= 0:
        raise ValueError(f"{name} debe ser un entero positivo")
    return result


def boolean(value, name):
    if value.lower() not in {"0", "1", "true", "false"}:
        raise ValueError(f"{name} debe ser 0, 1, true o false")
    return value.lower() in {"1", "true"}


@dataclass(frozen=True)
class Settings:
    base_url: str
    browser: str
    headed: bool
    width: int
    height: int
    timeout_ms: int
    navigation_timeout_ms: int
    evidence: bool
    artifacts: Path
    run_id: str

    @classmethod
    def from_env(cls, *, browser=None, headed=None, viewport=None):
        url = os.getenv("BASE_URL", "https://www.saucedemo.com").rstrip("/")
        parsed = urlsplit(url)
        if (
            parsed.scheme not in {"https", "http"}
            or not parsed.hostname
            or parsed.username
            or parsed.password
            or parsed.query
            or parsed.fragment
            or parsed.path
        ):
            raise ValueError("BASE_URL debe ser un origen http(s) sin credenciales, ruta, query ni fragmento")
        browser = browser or os.getenv("BROWSER", "chromium")
        if browser not in {"chromium", "firefox", "webkit"}:
            raise ValueError("BROWSER debe ser chromium, firefox o webkit")
        size = viewport or os.getenv("VIEWPORT", "1440x900")
        parts = size.lower().split("x")
        if len(parts) != 2:
            raise ValueError("VIEWPORT debe tener formato ANCHOxALTO")
        return cls(
            url,
            browser,
            boolean(os.getenv("HEADED", "0"), "HEADED") if headed is None else headed,
            positive_int(parts[0], "VIEWPORT width"),
            positive_int(parts[1], "VIEWPORT height"),
            positive_int(os.getenv("TIMEOUT_MS", "10000"), "TIMEOUT_MS"),
            positive_int(os.getenv("NAVIGATION_TIMEOUT_MS", "30000"), "NAVIGATION_TIMEOUT_MS"),
            boolean(os.getenv("CAPTURE_EVIDENCE", "0"), "CAPTURE_EVIDENCE"),
            Path(os.getenv("ARTIFACTS_DIR", "artifacts")),
            uuid4().hex,
        )

    @property
    def viewport(self):
        return {"width": self.width, "height": self.height}
