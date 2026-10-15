import os


def required_env(name):
    value = os.getenv(name)
    if not value:
        raise RuntimeError(
            f"Configura la variable de entorno {name}; o usa: python run_tests.py pytest --headed."
        )
    return value


def login_profile(login_page, profile):
    profiles = {
        "locked": (lambda: required_env("SAUCE_LOCKED_USERNAME"), lambda: None),
        "empty": (lambda: "", lambda: ""),
        "missing_password": (lambda: None, lambda: ""),
        "missing_user": (lambda: "", lambda: None),
        "unknown_user": (lambda: "invalid_test_user", lambda: None),
        "wrong_password": (lambda: None, lambda: "invalid_test_password"),
        "both_wrong": (lambda: "invalid_test_user", lambda: "invalid_test_password"),
    }
    user, password = profiles[profile]
    login_page.login(user(), password())
