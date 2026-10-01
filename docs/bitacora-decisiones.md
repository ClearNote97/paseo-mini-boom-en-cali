# 📓 Bitácora de decisiones

> **Fuente única de verdad** de las decisiones de diseño no triviales del proyecto
> (ver [`../README_AGENTS.md`](../README_AGENTS.md) §7). La memoria del agente **apunta aquí**, no guarda copia aparte.
>
> **Cómo se usa:** una entrada por decisión, en orden cronológico (la más antigua primero). Cada decisión
> tiene un ID `D-NNN` que **no se reutiliza**. Si una decisión reemplaza o revierte a otra, se enlazan por
> su ID y se actualiza el **estado** de ambas. El índice permite escanear sin leer todo.

## Índice

| ID | Decisión | Fecha | Estado |
|---|---|---|---|
| [D-001](#d-001--alcance-método-y-marco-de-puntuación-de-la-logística-del-viaje) | Alcance, método y marco de puntuación de la logística (transporte + estadía) | 2026-09-28 | Aceptada |
| [D-002](#d-002--recomendación-final-y-entregables) | Recomendación final (estadía + transporte) y paquete de 4 entregables | 2026-09-29 | Aceptada |
| [D-003](#d-003--escenarios-de-movilidad-y-análisis-de-horarios) | Cuatro escenarios de movilidad + análisis de horarios (el 4.º día) | 2026-09-30 | Aceptada |

---

## D-001 — Alcance, método y marco de puntuación de la logística del viaje

- **Fecha:** 2026-09-28
- **Estado:** Aceptada
- **Contexto:** Viaje grupal a Cali, 7 personas, 4 días / 3 noches (**30 oct – 2 nov 2026**, viernes a lunes → 3 noches de fin de semana, Halloween). Origen Cartagena (llegan en avión; la llegada NO es parte del alcance). Hay que decidir **transporte local** y **estadía** con presupuesto reducido y seguridad como prioridad.
- **Decisión:** Tratar la logística como un mini-proyecto de datos (recolectar → normalizar → puntuar → entregar shortlist). Recolección con **Playwright (Python)** sobre plataformas de reserva, complementada con investigación vía herramientas de búsqueda del asistente como *ground-truth*. Filtros duros + puntuación ponderada según los pesos de abajo. Entregable: 2–3 paquetes en `output/`.
- **Por qué:**
  - **Playwright** maneja sitios pesados en JS (Booking/Airbnb) con navegador real; es el estándar moderno (sobre Selenium) y valioso como aprendizaje / posible producto de GitHub. `requests`/BeautifulSoup se quedan cortos; Scrapy es overkill; no hay API abierta de hostales.
  - **División de trabajo por el entorno:** el shell del host no tiene egress a internet (hook de seguridad Helix con allowlist curada). El scraper se **ejecuta dentro del devcontainer** (donde viven `uv`, Python 3.14 y la red). El asistente aporta investigación paralela con sus propias herramientas para dar shortlist inmediato y validar el scraper.
  - **Seguridad como prioridad #1** del grupo → mayor peso y filtro duro de barrio.
- **Parámetros fijados:**
  - Presupuesto meta: **300–400k COP por persona** (transporte + estadía combinados). Techo con flex: **~480k** (+20%) si las amenidades lo justifican.
  - Camas: **mínimo 5** (comparten cama sin abusar); capacidad para 7.
  - Estadía cerca del Oeste / zona turística, con AC valorado positivamente. Amenidades valoradas: cerca de rumba/salsa, piscina/terraza, cocina, zonas comunes.
  - Transporte: alquiler de vehículo con **recogida en aeropuerto Palmaseca** (edad del conductor y tarjeta de crédito ya resueltos). Comparar contra Uber/DiDi/taxi.
- **Marco de puntuación:**
  - **Estadía** — filtros duros: `capacidad>=7`, `camas>=5`, disponible en fechas, barrio seguro (`senal_seguridad>=3`), `precio_pp<=480k`. Pesos: seguridad 30% · amenidades/comodidad (AC+) 20% · precio por persona 20% · cercanía a zona turística 12% · parqueadero 10% · ambiente social 8%.
  - **Transporte** — costo total 40% · capacidad 7+maletas 25% · seguro/depósito 15% · facilidad recogida aeropuerto 10% · reseñas agencia 10%.
- **Alternativas descartadas:**
  - Solo investigación manual del asistente (sin scraper): pierde el objetivo de aprendizaje y no deja artefacto reutilizable.
  - Scraping desde el host: bloqueado por el hook de egress; no se modifica la allowlist de seguridad.
  - Un solo entregable ordenado por precio (Económico/Equilibrado/Cómodo): reemplazado por **arquetipos por trade-off** (hostal social / casa entera / económico) porque el hostal vale por lo social, no solo por el precio.
- **Consecuencias:**
  - A favor: separación limpia de responsabilidades; la investigación paralela verifica al scraper (rigor); artefacto publicable.
  - En contra: el usuario ejecuta el scraper en su devcontainer (no lo corre el asistente); las plataformas tienen anti-bot (mitigado por bajo volumen y ritmo humano).

---

## D-002 — Recomendación final y entregables

- **Fecha:** 2026-09-29
- **Estado:** Aceptada
- **Contexto:** Cerrada la recolección (scraping Hostelworld sobre fechas reales + investigación de transporte), había que tomar postura y entregar el resultado en 4 formatos cruzados.
- **Decisión:** **Recomendación principal — Viajero Hostel & Salsa School (San Antonio) + van local autoconducido ≈ $407.000 por persona.** Alternativas: Patio del Río ($344.750, en meta), La Chanca ($244.850, piso), Casa entera ($455.000, comodidad). Transporte: alquiler local autoconducido (~$155k pp) sobre mostrador de aeropuerto (~$260k pp); evaluar *van con conductor*.
- **Por qué:** el Viajero es la única opción que satisface simultáneamente seguridad (San Antonio), piscina, AC, bar, rumba a pie y el factor social explícito (clases de salsa), quedando en el flex autorizado (≤$480k). El hallazgo del alquiler local bajó el transporte a la mitad y metió incluso la casa entera dentro del techo.
- **Ejecución real:** el scraper Playwright terminó ejecutándose por el asistente **dentro del devcontainer** vía `docker exec` (el host no tiene egress). Se instalaron `playwright`, `chromium`, `openpyxl`, `python-pptx`, `reportlab`, `pillow`.
- **Entregables (en `output/`):** `informe_completo.md`, `resumen_ejecutivo.pdf`, `resumen_resultados.xlsx` (una hoja por opción), `presentacion_cali_2026.pptx` (paleta carmesí/vinotinto + bandera de Cali). Generados desde una fuente única de datos en `src/generar_entregables.py`; se referencian entre sí.
- **Alternativas descartadas:** ordenar solo por precio (se prefirió arquetipos por trade-off); recomendar Patio del Río como principal (queda como alternativa "en meta" por no cubrir el factor social).
- **Consecuencias:** queda pendiente de verificación al reservar el supuesto precio por-persona-vs-habitación y la capacidad para 7 (camas ≥5), más la cotización por WhatsApp de la van local/con conductor. Urgencia: reservar pronto (finde de Halloween).

---

## D-003 — Escenarios de movilidad y análisis de horarios

- **Fecha:** 2026-09-30
- **Estado:** Aceptada (refina el transporte de [D-002])
- **Contexto:** El usuario quedó satisfecho con la estadía y pidió profundizar el transporte con horarios reales: salida 30 oct 7:00 am de Cartagena (llegada media mañana a Cali) y regreso en vuelo 9:00 pm del 2 nov. Referencia: búsqueda propia de Kayak (7 puestos exactos, CLO).
- **Decisión:** Modelar la movilidad como **cuatro escenarios** todo-incluido por persona: **S1** carro full aeropuerto (~$236k), **S2** 3 días + Uber última tarde (~$202k), **S3** agencia local con entrega en CLO (~$173k, **recomendado**), **S4** sin alquiler: transfers + Uber + 1 día van con conductor (~$126k). Recomendado **S3**. Los paquetes usan S3 como transporte de referencia; se documenta la sensibilidad (Viajero + cada escenario).
- **Hallazgo de horarios (el 4.º día):** Kayak cotiza mediodía→mediodía = 3 días ($1.053.522, el 7 puestos más barato). La ventana real cruza las 72 h y activa un 4.º día; el alquiler se cuenta en ciclos de 24 h desde la recogida (1 h de tolerancia, hora 25+ se cobra). Conservar el carro hasta las 7 pm del 2 cubre el hueco entre checkout y vuelo — su momento de mayor valor. Devolución fuera de horario: reservar con 24 h de aviso.
- **Por qué S3:** punto dulce entre costo y fricción — carro todos los días sin vueltas al aeropuerto, más barato que el mostrador; sujeto a confirmar que la agencia (Farallones / Car Rent del Caribe) entregue y reciba en CLO.
- **Revisión honesta:** el transporte real (~$126k–236k pp según escenario) es más alto que el ~$155k pp optimista de [D-002]. Los totales de los paquetes se actualizaron en los 4 entregables (v4).
- **Consecuencias:** el equilibrio recomendado (Viajero + S3) queda en ~$425k pp (flex); S4 lo baja a ~$378k (meta) y S1 lo sube a ~$488k (excede techo). Pendiente: confirmación por WhatsApp de entrega en CLO y tarifa del 4.º día. Se corrigió un bug de maquetación en el PDF (celdas de tabla ahora envuelven texto con Paragraph).
- **Actualización v5 (2026-09-30):** confirmado que la entrega en el aeropuerto SÍ está disponible en agencias locales (Farallones tiene oficina en el aeropuerto; WayCarCali hace domicilio gratis al aeropuerto para alquileres de 3+ días) — se elimina el "sujeto a confirmar" sobre el punto de recogida. La recomendación de movilidad se replanteó en lenguaje llano (sin siglas S1–S4 ni "CLO") a "carro propio todo el viaje, recogido en el aeropuerto" (~$150k pp; total Viajero+carro ≈ $402k). Al informe `.md` se le agregó **índice** y la sección de **metodología** (se habían perdido en v4). Respuesta directa a la pregunta del usuario: el carro se recoge **en el aeropuerto**, no en la ciudad.

---

<!-- ─────────────────────────────────────────────────────────────────────────────
PLANTILLA PARA UNA NUEVA DECISIÓN
(copia el bloque de abajo, quítale los comentarios, asígnale el número de ID y
agrégalo también a la tabla del Índice de arriba)

## D-NNN — <título corto de la decisión>

- **Fecha:** AAAA-MM-DD
- **Estado:** Aceptada          <!-- Aceptada | Reemplaza a D-XXX | Reemplazada por D-YYY | Revertida -->
- **Contexto:** <qué problema o disyuntiva la motivó>
- **Decisión:** <qué se decidió, en una frase>
- **Por qué:** <la razón principal y los criterios considerados>
- **Alternativas descartadas:** <qué otras opciones se evaluaron y por qué no>
- **Consecuencias:** <qué implica, a favor y en contra>

───────────────────────────────────────────────────────────────────────────── -->
