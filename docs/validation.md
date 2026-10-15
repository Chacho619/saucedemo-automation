# Validación de robustez y escalabilidad

Validación local en Windows y Python 3.12, 15 de octubre de 2026. Credenciales públicas de SauceDemo en variables del proceso; evidencias desactivadas.

| Informe | Pruebas | Fallos | Errores | Segundos |
|---|---:|---:|---:|---:|
| robust-chromium.xml | 70 | 0 | 0 | 74.10 |
| robust-unit.xml | 36 | 0 | 0 | 0.69 |
| robust-firefox.xml | 38 | 0 | 0 | 53.38 |
| robust-webkit.xml | 38 | 0 | 0 | 29.74 |
| robust-mobile.xml | 32 | 0 | 0 | 56.86 |
| robust-behave/TESTS-compra.xml | 3 | 0 | 0 | 2.30 |

Chromium: ejecución completa en dos trabajadores (incluía 32 unitarias al momento de esa ejecución, 6 contratos HTML local y 32 E2E). Después se añadieron cuatro pruebas unitarias de infraestructura: las 36 unitarias finales pasaron por separado. Firefox y WebKit: 32 E2E + 6 contratos, dos trabajadores. Vista móvil Chromium 390x844: 32 E2E, dos trabajadores. Behave Chromium: 3 escenarios, 10 pasos aprobados.

Ruff lint, Ruff format --check y pip check aprobados. El workflow YAML y sus contratos se validaron localmente; GitHub Actions no se ejecutó ni se activó porque no hay repositorio remoto configurado. No se validaron Linux, Safari real, dispositivos físicos ni comparación visual.

## Cobertura de la matriz original

- Automatizado: 46
- Manual pendiente: 4
- Parcial: 13
- Pendiente: 50
- Requiere requisito: 17

Son estados de automatización, no porcentajes de aprobación de los 130 casos. La suite nueva añade pruebas de infraestructura que no son casos funcionales de la matriz.

La primera ejecución local de unitarias encontró una restricción de permisos en el directorio temporal del sandbox; se volvió a ejecutar con TEMP/TMP apuntando a work/tmp dentro del workspace. No fue un fallo de la aplicación ni se cambió su código para ocultarlo.
