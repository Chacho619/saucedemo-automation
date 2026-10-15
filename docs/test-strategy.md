# Estrategia de pruebas basada en riesgo

## Objetivo y alcance

Esta estrategia usa los 130 casos de `traceability.csv` para priorizar validación y
definir decisiones de liberación. Está pensada para SauceDemo y sus flujos de compra
simulados; no implica que la demo procese pagos reales ni que sustituya una estrategia
para otro producto.

Los estados de la matriz describen la cobertura, no el resultado de una ejecución:
**Automatizado** o **Parcial** no significa que una prueba haya pasado en el commit
candidato. Consultar el reporte de CI y `validation.md` para conocer las ejecuciones
realizadas y sus límites.

## Evaluación y niveles de riesgo

Cada grupo recibe dos estimaciones de 1 a 5:

- **Impacto (I):** efecto en el usuario o el negocio si falla el flujo.
- **Probabilidad (P):** posibilidad estimada de que un cambio o regresión afecte el
  comportamiento.
- **Puntaje:** `I × P`. Es una priorización inicial, no una frecuencia de fallos
  observada; revisar los valores después de incidentes, cambios de producto o nuevos
  requisitos.

| Puntaje | Prioridad | Tratamiento |
|---:|---|---|
| 15–25 | P1 — crítico | Validar en cada candidato de liberación; un fallo o una brecha de cobertura bloquea la aprobación. |
| 8–14 | P2 — alto | Ejecutar en la matriz definida; documentar y aceptar explícitamente el riesgo residual para diferir cobertura. |
| 1–7 | P3 — normal | Ejecutar según cambios y regresión periódica; diferimientos no deben afectar un flujo P1. |

Una vulnerabilidad confirmada, exposición de secretos o defecto de integridad de
transacción bloquea la liberación independientemente del puntaje. Si el requisito es
ambiguo, no se inventa el resultado esperado: se aclara con producto y se vuelve a
evaluar el riesgo antes de aprobar.

## Registro de riesgos priorizados

Los IDs de cada fila son los casos de `traceability.csv`. Las prioridades son por
flujo; las pruebas existentes solo cubren la parte descrita en el estado y las
observaciones de esa matriz.

| Prioridad | Riesgo y casos | I × P | Cobertura y tratamiento |
|---|---|---:|---|
| P1 | Acceso: un usuario válido no puede entrar, una credencial inválida obtiene acceso o falla la validación. `LOG-02–09`. | 5 × 4 = 20 | Automatizados. Mantener el login válido y las variantes de rechazo en el smoke obligatorio. |
| P1 | Protección de sesión: rutas privadas quedan expuestas o una sesión cerrada conserva acceso. `SES-01–06`. | 5 × 3 = 15 | `SES-05` sigue pendiente; completar navegación atrás después del logout o justificar el requisito antes de cerrar esta brecha. |
| P1 | Carrito: artículos, cantidades/contador o selección no corresponden a lo que se pretende comprar. `CAR-02–08`, `CAR-15`. | 5 × 4 = 20 | `CAR-05–07` son parciales; completar comprobaciones de transiciones, datos y eliminación selectiva. `CAR-15` está automatizado. |
| P1 | Datos requeridos de checkout: datos incompletos dejan continuar o bloquean una compra válida. `INF-01–05`. | 5 × 3 = 15 | Automatizados. Mantener el envío válido y cada validación requerida en la regresión crítica. |
| P1 | Precio y finalización: subtotal, impuesto, total o resultado final difieren de la selección. `FIN-01–07`, `FIN-10–13`. | 5 × 3 = 15 | `FIN-11` y `FIN-13` son parciales; `FIN-12` está pendiente. Completar la verificación del carrito vacío y la compra repetida antes de afirmar cobertura P1 completa. La tasa esperada debe estar aprobada para el entorno. |
| P2 | Catálogo y detalle: producto, precio, orden o información visible no corresponde. `CAT-01–12`, `DET-01–08`. | 4 × 3 = 12 | Cerrar los casos parciales que impacten identidad/precio. Aclarar las reglas de orden y persistencia antes de convertirlas en criterios de aceptación. |
| P2 | Variantes de entrada e interacción del checkout, fuera de los campos requeridos P1. `LOG-01`, `LOG-10–18`, `SES-07–12`, `CAR-01`, `CAR-09–14`, `CAR-16`, `INF-06–16`, `FIN-08–09`, `FIN-14`. | 4 × 2–3 = 8–12 | Priorizar errores de validación y datos no preservados. Los casos marcados `Requiere requisito` no se consideran aprobados hasta definir el comportamiento. |
| P2 | Perfiles alternativos de usuario. `USR-03–06`. | 3 × 3 = 9 | Mantener como regresión de perfiles; `USR-06` requiere evaluación visual manual. |
| P2 | Accesibilidad, compatibilidad y otros atributos de calidad. `NFR-01–10`. | 4 × 3 = 12 | Incorporar pruebas de teclado/foco y definir umbrales de tiempos, navegadores, móvil y recuperación antes de usarlos como gate. WebKit no certifica Safari real. |
| P2 | Controles de seguridad e integridad. `SEC-01–04`. | 5 × 2 = 10 | La matriz los tiene pendientes o sujetos a requisito. No concluir que existe una vulnerabilidad por falta de prueba; evaluar requisitos y alcance. Todo hallazgo confirmado bloquea, sin importar el puntaje. |
| P3 | Menú y catálogo dinámico de la demo. `MEN-01–06`, `DYN-01–08`. | 2 × 2 = 4 | Regresión según alcance del cambio. Promover a P1/P2 si el producto o un requisito convierte estos flujos en críticos. |

## Criterios de aprobación y bloqueo

### Pull request

**Aprobar para integración únicamente si:**

1. El job `quality` termina en verde: Ruff lint, formato, pruebas unitarias y
   contratos de páginas con HTML local.
2. No hay regresiones nuevas en casos tocados; las pruebas nuevas mantienen vínculo
   verificable con sus IDs de trazabilidad.
3. Un cambio que afecte un flujo P1 incluye evidencia E2E del flujo afectado, en la
   ejecución segura disponible para el equipo.
4. Se revisaron fallos, skips y artefactos; no se ocultan fallos mediante reintentos,
   xfail o cambios que reduzcan la aserción sin una justificación aprobada.

**Bloquear** ante job requerido fallido, defecto P1 reproducible, cambio no validado
que afecte un flujo P1, o credenciales/datos sensibles expuestos. Los pull requests
desde forks no deben recibir secretos. La política de ramas de GitHub debe exigir el
job `quality`; configurar ese requisito en GitHub es una acción del administrador,
no algo garantizado por el workflow.

### Candidato de liberación

**Aprobar únicamente cuando se cumpla todo lo siguiente:**

1. Calidad, unitarias y contratos locales están en verde en el commit exacto del
   candidato.
2. No hay defectos P1 abiertos; todos los casos P1 tienen criterio esperado acordado,
   cobertura completa y ejecución aprobada. Un estado `Parcial`, `Pendiente` o
   `Requiere requisito` no equivale a cobertura completa.
3. Login válido/rechazado, protección de sesión, compra con uno y varios artículos,
   validaciones requeridas, totales y confirmación de compra pasan en E2E.
4. Pasa la matriz soportada para la versión: Chromium, Firefox, WebKit y viewport
   390x844. La afirmación se limita a esos motores/viewports; no supone dispositivos
   físicos ni Safari real.
5. No hay hallazgos de seguridad confirmados ni P1 conocidos. Cada defecto P2
   pendiente tiene aceptación explícita del riesgo, responsable, mitigación y fecha
   de revisión.
6. Si cambia una expectativa de producto, requisito, tasa/impuesto o soporte de
   navegador, la decisión está documentada y aprobada antes de comparar resultados.

**Bloquear** si falla cualquier criterio anterior, hay una prueba P1 fallida/no
ejecutada, el candidato no coincide con el commit probado o no se puede distinguir
un defecto de una falla del entorno. Repetir una ejecución fallida puede ayudar a
diagnosticar, pero no convierte el primer fallo en aprobación: investigar y dejar
evidencia de causa y resolución.

## Estado del proyecto y brechas del gate

La última foto documentada en `validation.md` registra 46 casos automatizados, 13
parciales, 50 pendientes, 4 manuales pendientes y 17 que requieren requisito. Entre
los P1, `SES-05` y `FIN-12` están pendientes; `CAR-05–07`, `FIN-11` y `FIN-13` son
parciales. Por tanto, bajo el criterio estricto de esta estrategia, la matriz aún no
demuestra cobertura P1 completa. Es una brecha de evidencia/cobertura, no una
afirmación de que la aplicación demo tenga esos defectos.

El workflow ejecuta calidad en pull requests; E2E requiere secretos y se omite en
pull requests. La matriz de navegadores y Behave se ejecuta en push a `main`/`master`
o mediante `workflow_dispatch`, es decir, puede detectar una regresión después de
integrar. Antes de usarlo como gate de liberación, hacer obligatoria la verificación
`quality` en protección de rama y ejecutar la matriz E2E en un commit candidato antes
de etiquetar/publicar la versión. Mantener los secretos fuera de pull requests de
forks.

Este proyecto no define actualmente despliegue, versionado/release automático ni
protección de rama. Por ello los criterios de candidato son una política explícita
para aplicar, no una automatización ya configurada.
