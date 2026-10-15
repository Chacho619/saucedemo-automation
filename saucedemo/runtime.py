"""Ciclo de vida seguro, incluso si la preparación o evidencia falla."""

import hashlib
import re
import warnings
from contextlib import ExitStack
from uuid import uuid4

from playwright.sync_api import expect

from saucedemo.app import Shop


class BrowserSession:
    def __init__(self, browser, settings):
        self.browser = browser
        self.settings = settings
        self.stack = ExitStack()
        self.context = None
        self.page = None
        self.tracing = False

    def start(self):
        try:
            self.context = self.browser.new_context(viewport=self.settings.viewport)
            self.stack.callback(self._close_context)
            if self.settings.evidence:
                self.context.tracing.start(screenshots=True, snapshots=True, sources=False)
                self.tracing = True
            expect.set_options(timeout=self.settings.timeout_ms)
            self.page = self.context.new_page()
            self.page.set_default_timeout(self.settings.timeout_ms)
            self.page.set_default_navigation_timeout(self.settings.navigation_timeout_ms)
            return Shop(self.page, self.settings)
        except BaseException:
            self.close()
            raise

    def _close_context(self):
        try:
            self.context.close()
        except Exception:
            warnings.warn("No se pudo cerrar el contexto del navegador.", RuntimeWarning, stacklevel=2)

    def artifact_folder(self, runner, identity, worker):
        label = re.sub(r"[^a-zA-Z0-9_-]", "_", identity)[:70]
        digest = hashlib.sha256(identity.encode()).hexdigest()[:10]
        worker = re.sub(r"[^a-zA-Z0-9_-]", "_", worker)
        return (
            self.settings.artifacts
            / runner
            / self.settings.run_id
            / worker
            / f"{label}-{digest}-{uuid4().hex[:8]}"
        )

    def close(self, failed=False, runner="pytest", identity="test", worker="main"):
        try:
            if self.context is not None and self.tracing:
                folder = self.artifact_folder(runner, identity, worker) if failed else None
                try:
                    if folder:
                        folder.mkdir(parents=True, exist_ok=True)
                        if self.page is not None:
                            self.page.screenshot(path=str(folder / "failure.png"), full_page=True)
                except Exception:
                    warnings.warn("No se pudo guardar la captura de fallo.", RuntimeWarning, stacklevel=2)
                finally:
                    try:
                        self.context.tracing.stop(**({"path": str(folder / "trace.zip")} if folder else {}))
                    except Exception:
                        warnings.warn("No se pudo guardar/cerrar la traza.", RuntimeWarning, stacklevel=2)
                    self.tracing = False
        finally:
            self.stack.close()
            self.context = None
            self.page = None
