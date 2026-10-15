# SauceDemo: Python, Playwright, pytest y Behave con POM

Proyecto para VS Code. Abre esta carpeta completa y selecciona `.venv/Scripts/python.exe` como intérprete. Instala las extensiones Python y Python Debugger de Microsoft.

## Instalar

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.\.venv\Scripts\python.exe -m playwright install chromium firefox webkit
```

Python objetivo: 3.12. `requirements-lock.txt` fija las versiones validadas; `requirements.txt` declara los rangos para actualizaciones deliberadas. No actualices el lock sin ejecutar calidad y la matriz de navegadores. No es necesario activar el entorno ni cambiar la política de PowerShell.

## Ejecutar en consola

```powershell
# Suite completa, dos procesos y navegador visible
.\.venv\Scripts\python.exe run_tests.py pytest --headed -n 2

# Solo flujo principal
.\.venv\Scripts\python.exe run_tests.py pytest -m smoke --headed

# Una prueba
.\.venv\Scripts\python.exe run_tests.py pytest tests/test_shop.py::test_LOG_02_login --headed

# BDD
.\.venv\Scripts\python.exe run_tests.py behave

# Firefox y vista móvil (viewport, no emulación de dispositivo)
.\.venv\Scripts\python.exe run_tests.py pytest -m e2e --browser firefox -n 2
.\.venv\Scripts\python.exe run_tests.py pytest -m e2e --viewport 390x844 -n 2
```

El ejecutor solicita usuario estándar, usuario bloqueado y contraseña si faltan. Usa los valores públicos del login de SauceDemo. La contraseña se introduce oculta y se pasa solo al proceso hijo: no se escribe en archivos, argumentos ni historial. En CI se requieren variables ya configuradas; no hay valores de credenciales por defecto.

`python -m pytest` y `python -m behave` siguen funcionando si configuras previamente `SAUCE_USERNAME`, `SAUCE_LOCKED_USERNAME`, `SAUCE_PASSWORD`. El fallo por variables faltantes ocurre antes de enviar credenciales y no es un defecto del sitio. `.env.example` es una plantilla sin secretos; no se carga automáticamente.

Para configurar variables manualmente:

```powershell
$env:SAUCE_USERNAME = Read-Host 'Usuario estándar'
$env:SAUCE_LOCKED_USERNAME = Read-Host 'Usuario bloqueado'
$securePassword = Read-Host 'Contraseña' -AsSecureString
$env:SAUCE_PASSWORD = [System.Net.NetworkCredential]::new('', $securePassword).Password
Remove-Variable securePassword
```

VS Code debe heredar el entorno para ejecutar pruebas desde su panel Testing. F5 usa el ejecutor interactivo. Al terminar: `Remove-Item Env:SAUCE_PASSWORD`.

## Calidad y pruebas del framework

No requieren credenciales ni red:

```powershell
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m ruff format --check .
.\.venv\Scripts\python.exe -m pytest -m unit
```

Generación de reportes Allure para pytest y Behave:

```powershell
# pytest ya incluye --alluredir=allure-results en pytest.ini
.\.venv\Scripts\python.exe run_tests.py pytest -m unit

# Behave requiere el formatter de Allure explícito
.\.venv\Scripts\python.exe run_tests.py behave -f allure_behave.formatter:AllureFormatter -o allure-results

# Si tienes Allure CLI instalado, convierte los JSON a HTML
allure generate allure-results --clean -o allure-report
allure open allure-report
```

Los contratos de páginas requieren navegador instalado, pero usan HTML local y no el sitio:

```powershell
.\.venv\Scripts\python.exe -m pytest -m component
```

Se comprueban configuración inválida, prioridad CLI/entorno, cálculo y redondeo, carga de datasets, preparación parcial, fallo de capturas/trazas, nombres de evidencias, ejecutor sin eco de contraseña, argumentos y coherencia de trazabilidad/CI. Los contratos rechazan importes con coincidencias parciales y verifican la espera de listas.

## Arquitectura

- `saucedemo/pages/`: pantallas; selectores, acciones y verificaciones de UI.
- `saucedemo/components/header.py`: encabezado compartido.
- `saucedemo/app.py`: contenedor de Page Objects para un contexto.
- `saucedemo/settings.py`: configuración validada común a pytest y Behave.
- `saucedemo/runtime.py`: preparación, evidencias y cierre; cleanup desde que se crea el contexto.
- `saucedemo/config.py`: credenciales externas y perfiles de prueba.
- `saucedemo/rules.py`: cálculo esperado y validación del catálogo, fuera de páginas.
- `saucedemo/datasets/saucedemo.json`: productos y tasa esperada de la demo.
- `tests/test_shop.py`: pruebas funcionales parametrizadas.
- `tests/unit/`: infraestructura sin navegador.
- `tests/test_page_contracts.py`: verificaciones de páginas sobre HTML local.
- `features/`: Gherkin en español y pasos que comparten POM.
- `docs/traceability.csv`: cobertura de los 130 casos originales.
- `.github/workflows/tests.yml`: calidad y matriz de ejecución para GitHub Actions.

pytest y Behave son ejecutores independientes. No se deben ejecutar los steps de Behave desde pytest. Los contextos nuevos aíslan cookies y almacenamiento; cada trabajador pytest tiene su navegador. La demo mantiene su carrito por contexto. Para otra aplicación con estado en servidor se requieren cuentas/datos exclusivos por trabajador antes de habilitar paralelismo. Behave se ejecuta secuencialmente dentro de cada combinación de CI.

## Configuración centralizada

| Variable | Predeterminado | Uso |
|---|---|---|
| BASE_URL | https://www.saucedemo.com | Origen http(s), sin credenciales/ruta/query |
| BROWSER | chromium | chromium, firefox o webkit |
| HEADED | 0 | Mostrar navegador con 1 |
| VIEWPORT | 1440x900 | Ancho x alto |
| TIMEOUT_MS | 10000 | Acciones y assertions |
| NAVIGATION_TIMEOUT_MS | 30000 | Navegación |
| CAPTURE_EVIDENCE | 0 | Evidencias opcionales |
| ARTIFACTS_DIR | artifacts | Resultados locales |
| CATALOG_PATH | Dataset incluido | JSON alternativo con products y tax_rate |

pytest permite sobrescribir entorno con `--browser`, `--headed`, `--viewport`. Behave usa las mismas variables y Settings. Cada ejecución/contexto usa rutas de evidencias con identificador único, trabajador, hash del caso y sufijo único; no sobrescribe archivos de otros trabajadores. Para JUnit de ejecuciones simultáneas usa nombres distintos o directorios distintos por job.

El catálogo estándar incluye seis productos, pero `assert_loaded()` solo valida que la pantalla esté disponible. La cantidad y los valores esperados pertenecen al dataset/test. Impuesto del 8% es una referencia de la demo: confirmar con producto para otro entorno y cambiar `tax_rate` del dataset aprobado. No se deriva el valor esperado del mismo DOM que se verifica.

## Evidencias y seguridad

```powershell
$env:CAPTURE_EVIDENCE='1'
.\.venv\Scripts\python.exe run_tests.py pytest
.\.venv\Scripts\python.exe -m playwright show-trace RUTA_DEL_TRACE.zip
```

Capturas y trazas están desactivadas por defecto. Al activarlas solo se guardan en fallos; una traza puede incluir valores, DOM y tráfico aunque `sources=False`. No hay redacción completa garantizada. Utiliza datos ficticios, revisa artefactos antes de compartirlos y aplica acceso restringido/retención. CI publica únicamente XML con retención de siete días, no trazas ni capturas. Los reportes también necesitan revisión si se amplían pruebas con datos privados. `.gitignore` evita nuevos archivos locales, pero no limpia historial Git ni archivos previamente versionados.

## CI y matriz

El workflow está preparado para un repositorio GitHub cuya raíz sea esta carpeta. No está publicado ni activado desde este chat. Para activarlo:

1. Coloca el proyecto en el repositorio, incluyendo `.github/workflows/tests.yml` en su raíz.
2. Configura Repository Secrets: `SAUCE_USERNAME`, `SAUCE_LOCKED_USERNAME`, `SAUCE_PASSWORD` con cuentas de prueba.
3. Revisa permisos, ramas `main/master` y políticas de tu equipo; ejecuta workflow_dispatch.

En pull requests solo se ejecutan calidad y unitarias sin secretos. En push a main/master o ejecución manual, después de calidad, se ejecuta la matriz E2E:

| Navegador | Viewport | pytest | Behave |
|---|---|---|---|
| Chromium | 1440x900 | E2E + contratos, 2 workers | 3 escenarios |
| Firefox | 1440x900 | E2E + contratos, 2 workers | 3 escenarios |
| WebKit | 1440x900 | E2E + contratos, 2 workers | 3 escenarios |
| Chromium | 390x844 | E2E + contratos, 2 workers | 3 escenarios |

Límite: dos jobs de matriz simultáneos; timeout por job y fail-fast desactivado. Dependencias del sistema se instalan con Playwright en Linux. WebKit no reemplaza validar Safari real; un viewport estrecho no equivale a un dispositivo móvil real ni verifica automáticamente solapamientos o contraste.

## Cobertura y ampliación

`docs/traceability.csv` contiene 130 IDs únicos, estado, referencia de prueba y observaciones. Automatizado no significa ejecutado/aprobado en cualquier entorno: consulta XML y `docs/validation.md`. Los casos parciales, manuales y sujetos a requisito no se contabilizan como cobertura completa. Los nombres históricos de algunas funciones agrupan rangos de IDs; la matriz es la fuente de cobertura efectiva.

Para ampliar: añade expectativas al test y selectores/acciones a su Page Object, parametriza datos, actualiza la matriz, ejecuta unitarias/contratos y luego el flujo afectado. No añadas reintentos o xfail para ocultar defectos. Los 130 casos no están todos automatizados: seguridad, rendimiento, accesibilidad completa, perfiles especiales y Dynamic Catalog siguen según la matriz.

Fuentes del diseño CI/paralelismo: https://playwright.dev/python/docs/ci y https://pytest-xdist.readthedocs.io/en/stable/how-to.html.
