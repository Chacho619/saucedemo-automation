from unittest.mock import MagicMock, patch

import pytest

from saucedemo.runtime import BrowserSession
from saucedemo.settings import Settings

pytestmark = pytest.mark.unit


def test_context_closed_when_page_creation_fails():
    browser = MagicMock()
    browser.new_context.return_value.new_page.side_effect = RuntimeError("page creation failed")
    session = BrowserSession(browser, Settings.from_env())
    with pytest.raises(RuntimeError, match="page creation failed"):
        session.start()
    browser.new_context.return_value.close.assert_called_once()
    session.close()
    browser.new_context.return_value.close.assert_called_once()


def test_context_closed_when_shop_creation_fails():
    browser = MagicMock()
    session = BrowserSession(browser, Settings.from_env())
    with patch("saucedemo.runtime.Shop", side_effect=RuntimeError("shop failed")):
        with pytest.raises(RuntimeError, match="shop failed"):
            session.start()
    browser.new_context.return_value.close.assert_called_once()


def test_evidence_failure_does_not_prevent_trace_or_context_close(monkeypatch, tmp_path):
    monkeypatch.setenv("CAPTURE_EVIDENCE", "1")
    monkeypatch.setenv("ARTIFACTS_DIR", str(tmp_path))
    browser = MagicMock()
    session = BrowserSession(browser, Settings.from_env())
    session.start()
    session.page.screenshot.side_effect = RuntimeError("screenshot failed")
    with pytest.warns(RuntimeWarning, match="captura"):
        session.close(failed=True)
    browser.new_context.return_value.tracing.stop.assert_called_once()
    browser.new_context.return_value.close.assert_called_once()


def test_artifact_names_do_not_collide():
    session = BrowserSession(MagicMock(), Settings.from_env())
    paths = {session.artifact_folder("pytest", "a/b", worker) for worker in ["gw0", "gw1", "gw0"]}
    assert len(paths) == 3
    assert all(".." not in str(path) for path in paths)


def test_context_closed_when_trace_start_fails(monkeypatch):
    monkeypatch.setenv("CAPTURE_EVIDENCE", "1")
    browser = MagicMock()
    browser.new_context.return_value.tracing.start.side_effect = RuntimeError("trace failed")
    session = BrowserSession(browser, Settings.from_env())
    with pytest.raises(RuntimeError, match="trace failed"):
        session.start()
    browser.new_context.return_value.close.assert_called_once()


def test_trace_stop_failure_does_not_prevent_context_close(monkeypatch):
    monkeypatch.setenv("CAPTURE_EVIDENCE", "1")
    browser = MagicMock()
    session = BrowserSession(browser, Settings.from_env())
    session.start()
    browser.new_context.return_value.tracing.stop.side_effect = RuntimeError("trace stop failed")
    with pytest.warns(RuntimeWarning, match="traza"):
        session.close()
    browser.new_context.return_value.close.assert_called_once()
