"""Ejecutor interactivo: credenciales en memoria, nunca en argumentos ni archivos."""

import argparse
import getpass
import os
import subprocess
import sys
import warnings
from pathlib import Path

CREDENTIALS = (
    ("SAUCE_USERNAME", "Usuario estándar de prueba: "),
    ("SAUCE_LOCKED_USERNAME", "Usuario bloqueado de prueba: "),
    ("SAUCE_PASSWORD", "Contraseña de prueba (entrada oculta): "),
)


def execution_environment():
    environment = os.environ.copy()
    missing = [(key, prompt) for key, prompt in CREDENTIALS if not environment.get(key)]
    if missing and not sys.stdin.isatty():
        names = ", ".join(key for key, _ in missing)
        raise ValueError(
            f"Faltan variables: {names}. Configúralas en el entorno de CI o ejecuta desde una terminal interactiva."
        )
    for key, prompt in missing:
        if key == "SAUCE_PASSWORD":
            # No permitir que getpass recurra a entrada visible.
            with warnings.catch_warnings():
                warnings.simplefilter("error", getpass.GetPassWarning)
                value = getpass.getpass(prompt)
        else:
            value = input(prompt).strip()
        if not value:
            raise ValueError(f"{key} no puede quedar vacía. No se iniciaron pruebas.")
        environment[key] = value
    return environment


def main():
    parser = argparse.ArgumentParser(description="Ejecutar pytest o Behave con credenciales de prueba.")
    parser.add_argument("runner", choices=["pytest", "behave"])
    options, forwarded = parser.parse_known_args()
    try:
        environment = execution_environment()
    except (ValueError, EOFError, getpass.GetPassWarning) as error:
        print(f"Configuración: {error}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("\nEjecución cancelada.", file=sys.stderr)
        return 130
    try:
        return subprocess.call(
            [sys.executable, "-m", options.runner, *forwarded],
            cwd=Path(__file__).resolve().parent,
            env=environment,
        )
    finally:
        for key, _ in CREDENTIALS:
            environment.pop(key, None)


if __name__ == "__main__":
    raise SystemExit(main())
