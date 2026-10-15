import getpass
from unittest.mock import patch

import pytest

import run_tests

pytestmark = pytest.mark.unit


@pytest.fixture(autouse=True)
def clear_credentials(monkeypatch):
    for name, _ in run_tests.CREDENTIALS:
        monkeypatch.delenv(name, raising=False)


def test_interactive_credentials_not_saved_to_parent_environment(monkeypatch):
    with (
        patch("sys.stdin.isatty", return_value=True),
        patch("builtins.input", side_effect=["demo", "locked"]),
        patch("getpass.getpass", return_value="fake-secret"),
    ):
        result = run_tests.execution_environment()
    assert result["SAUCE_PASSWORD"] == "fake-secret"
    assert all(not run_tests.os.getenv(name) for name, _ in run_tests.CREDENTIALS)


def test_ci_missing_credentials_fails_without_prompt():
    with patch("sys.stdin.isatty", return_value=False), pytest.raises(ValueError, match="SAUCE_PASSWORD"):
        run_tests.execution_environment()


def test_existing_credentials_do_not_prompt(monkeypatch):
    for name, _ in run_tests.CREDENTIALS:
        monkeypatch.setenv(name, "fake")
    with patch("builtins.input") as prompt, patch("getpass.getpass") as password:
        run_tests.execution_environment()
    prompt.assert_not_called()
    password.assert_not_called()


def test_password_echo_fallback_is_rejected():
    with (
        patch("sys.stdin.isatty", return_value=True),
        patch("builtins.input", side_effect=["demo", "locked"]),
        patch("getpass.getpass", side_effect=getpass.GetPassWarning("no hidden input")),
    ):
        with pytest.raises(getpass.GetPassWarning):
            run_tests.execution_environment()


def test_runner_forwards_arguments_and_cleans_child_credentials(monkeypatch):
    for name, _ in run_tests.CREDENTIALS:
        monkeypatch.setenv(name, "fake")
    monkeypatch.setattr("sys.argv", ["run_tests.py", "pytest", "-n", "2"])
    with patch("subprocess.call", return_value=7) as call:
        assert run_tests.main() == 7
    assert call.call_args.args[0][-3:] == ["pytest", "-n", "2"]
    assert all(key not in call.call_args.kwargs["env"] for key, _ in run_tests.CREDENTIALS)
