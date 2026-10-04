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
| [D-004](#d-004--planeación-v2-cambio-de-horario-de-ida-llegada-de-noche) | Planeación v2: cambio de horario de ida (llegada de noche) → movilidad reajustada | 2026-10-01 | Aceptada |
| [D-005](#d-005--subsección-airbnb-casasaptos-enteros-con-datos-reales--la-dimensión-de-baños) | Subsección Airbnb (casas/aptos enteros) con datos reales + la dimensión de baños (informativa) | 2026-10-04 | Aceptada |

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

## D-004 — Planeación v2: cambio de horario de ida (llegada de noche)

- **Fecha:** 2026-10-01
- **Estado:** Aceptada (reajusta la movilidad de [D-002] y [D-003]; la estadía no cambia)
- **Contexto:** Cambió el vuelo de ida: ahora **sale 6:00 pm y llega 8:00 pm del 30 oct** (antes, media mañana). El regreso sigue igual (vuelo 9:00 pm del 2). El usuario pidió reformular solo movilidad y planear la v2.
- **Decisión:** Movilidad v2. **Recomendado: carro propio recogido en el aeropuerto esa misma noche** (el usuario eligió "varias salidas / libertad total" + "recoger de noche en el aeropuerto"), ~$180k pp → total Viajero + carro ≈ **$432k pp (flex)**. Alternativas: taxi oficial la 1ª noche + carro local el 31 (~$150k pp, evita manejar de noche y es más barato), o sin carro propio (~$125k pp, entra en meta). Palanca: si una agencia local confirma entrega nocturna en el aeropuerto, el carro propio baja a ~$140k pp.
- **Datos duros (horarios nocturnos):** el 30 oct es viernes; en el aeropuerto **Alamo y Localiza abren hasta las 10 pm** (L–V) → recogida a las ~9 pm factible; Avis/Budget cierran 5 pm. Recogida fuera de horario disponible reservando con 24 h. Taxis oficiales 24/7 (~$70k por carro, distintivo amarillo).
- **Impacto de costo:** la llegada de noche mete el viaje en **3 días de alquiler limpios** (recoger ~9 pm del 30, devolver ~7 pm del 2, bajo 72 h) — un día menos que antes; pero recoger de noche obliga a los mostradores que abren tarde (más caros que las locales), de ahí la palanca.
- **Pendiente:** WhatsApp a Farallones/WayCarCali (¿entregan en el aeropuerto hacia las 9 pm?) y reservar recogida fuera de horario en Alamo/Localiza como respaldo si el vuelo se retrasa.
- **Consecuencias:** 4 entregables regenerados a v2 desde la fuente única; estadía intacta; la recomendación global pasa de ~$402k (v1) a ~$432k pp (mostrador nocturno), con la palanca local para volver a ~$400k.

---

## D-005 — Subsección Airbnb (casas/aptos enteros) con datos reales + la dimensión de baños

- **Fecha:** 2026-10-04
- **Estado:** Aceptada (amplía la búsqueda de estadía de [D-001] y [D-002]; no cambia el puntaje ni el ranking)
- **Contexto:** Hablando con el grupo antes de la presentación, apareció una prioridad que no estaba explícita: **no compartir baño con extraños**. La idea de cuartos separados era tentadora justo por el tema de los baños. De ahí dos configuraciones aceptables: todos en una habitación privada para los siete, o cada habitación con baño propio — y, por encima de todo, la **casa o apartamento entero**, donde ningún baño se comparte. Se pidió además ser más explícitos con las mejores opciones de apto/casa.
- **Decisión:** (1) Agregar una **subsección de Airbnb** con opciones concretas de alojamiento entero, con **datos reales** (barrido Playwright), que cumplen los mismos criterios. (2) Incorporar los baños como **dimensión informativa** — columna "¿Baño compartido?" + nota —, **sin** filtro duro nuevo ni re-pesado: el puntaje y el ranking de hostales quedan **intactos** (lo decide el grupo).
- **Por qué:**
  - La privacidad de baños es un criterio real del grupo, pero meterlo como filtro/peso habría reordenado todo el puntaje y potencialmente volteado la recomendación a días de la presentación. Como dimensión informativa cumple el objetivo (visibilizar el punto) sin romper la trazabilidad del método ya aceptado.
  - Airbnb se eligió para el alojamiento entero porque es donde está la oferta de casas/aptos completos; se scrapeó con Playwright (anti-bot más agresivo que Hostelworld — por eso un scraper defensivo con screenshot + volcado de HTML).
- **Ejecución real:** nuevos scrapers `src/scrapers/explora_airbnb.py` (listados por zona segura, alojamiento entero, fechas reales, 7 adultos) y `explora_fichas_airbnb.py` (detalle de ficha: capacidad, habitaciones, camas, **baños**). Corridos dentro del devcontainer (`docker exec`); hubo que instalar el binario de Chromium y las libs del sistema (`playwright install-deps`). Los `*.json` de salida son artefactos intermedios (no se versionan); la data curada vive en `generar_entregables.py` (fuente única).
- **Hallazgos (datos reales, 30 oct–2 nov, 7 personas):**
  - Casa/apto **entero** desde **~$77k–$90k por persona** las 3 noches en San Antonio — **muy por debajo** del estimado conservador de $300k pp que la casa entera tenía en el puntaje (v1). La opción privada resultó, además, de las más económicas.
  - Flagship: *Casa de 4 Habitaciones – Terraza y Aire/C* (San Antonio, cabe 9, 5 camas, 1,5 baños del grupo, aire en el anuncio) → **$78.571 pp**; con carro propio local ≈ **$278.571 pp (DENTRO)**.
  - Contraejemplos útiles (por qué se miran baños y camas, no solo precio): *Casa Familiar 5 Hab* ($77k pp pero **1 baño para 11**) y *Apto El Ingenio 301* (3 camas < mínimo 5 y lejos de la rumba).
- **Alcance en los 4 entregables:** columna "¿Baño compartido?" en la tabla de estadía; nueva **subsección Airbnb** en el informe; hoja **"Airbnb (enteros)"** en el Excel; bloque Airbnb en el PDF; diapositiva nueva en la presentación. La lectura "Casa entera" pasó a mostrar el **precio real** ($278.571 DENTRO) en vez del estimado viejo ($500.000 EXCEDE), sin tocar el puntaje (que es display aparte, con el estimado congelado para no mover el ranking).
- **Alternativas descartadas:** baño como filtro duro + criterio con peso (re-balanceo a 100) — rechazado por el usuario para no mover el ranking antes de la presentación; investigación manual en vez de scrape — se prefirió el dato real.
- **Consecuencias:** la casa entera queda como alternativa fuerte y barata que resuelve los baños, sin desplazar la recomendación vigente (Viajero + carro local, por su ambiente social/salsa). Queda abierta la decisión del grupo entre **ambiente social (hostal)** y **privacidad + baños propios + menor costo (casa entera)**. Pendiente al reservar: tarifas de servicio/limpieza de Airbnb y confirmar aire/piscina marcados "según anuncio".

- **Actualización v2 (2026-10-04) — rebúsqueda en el occidente + puntaje a las casas:** al grupo no le convencieron las primeras casas y pidió apuntar al **occidente, cerca de la zona de actividades**, y **aplicarles el mismo ranking** para comparar con referencia visual. Se decidió:
  - **Rebarrido** del occidente/zona de actividades (El Peñón, Granada, Santa Teresita, San Antonio; se descartaron derivas rurales/sur que Airbnb devolvió por geocoding). El scraper ahora hace scroll para cargar más tarjetas; el de fichas extrae amenidades (aire/piscina/parqueadero) y rating (con un recorte del carrusel de "similares" que contaminaba la detección).
  - **Mismo puntaje 0–100** (seguridad 30 · amenidades 20 · precio 20 · cercanía 12 · parqueadero 10 · social 8) aplicado a las casas en un **ranking SEPARADO**: el precio se normaliza **dentro** del set Airbnb y el *social* las castiga (sin vida de hostal). **Los hostales quedan 100% intactos** (elección del usuario sobre la alternativa unificada, que habría movido sus puntajes por la normalización de precio).
  - **Referencia visual:** gráfico de barras del ranking Airbnb en la presentación (mismo estilo que el de hostales) + columna **Puntaje** en informe/Excel/PDF. Se corrigió, de paso, un título espurio ("v") que LibreOffice pintaba en ambos gráficos (`has_title = False`).
  - **Resultado del ranking:** 1º *Casa amoblada para 7 personas con garaje* (San Antonio, **94.6** — 2,5 baños, garaje, barata), 2º *Casa Bella en la bohemia San Antonio* (89.7), 3º *Casa de 4 Hab – Terraza y Aire* (89.2). Mejor casa + carro local ≈ **$290.714 pp (DENTRO)**. Se marcó *Las Flores* como fuera del occidente (norte, cerca de Menga) y se movieron a "no cumplen" las de <5 camas o 1 baño. Amenidades siguen "según el anuncio" (confirmar al reservar).

- **Actualización v3 (2026-10-04) — el grupo revisó las casas una por una y las ubicó mal:** varias que "parecían" del oeste estaban en el **este** (Casa 4 Hab, Casa 8 "Granada"), el **sur** (Apto moderno, lejísimos) o eran **Las Flores = este**; la Casa Bella (la mejor ubicada) resultó **sin disponibilidad para el 30**; y la de piscina privada se sale del presupuesto. Pidió apuntar al **noroeste/oeste** de verdad. Se decidió:
  - **Verificar la ubicación por COORDENADAS de la ficha** (no por el título, que engaña): `explora_fichas_airbnb.py` ahora extrae lat/lng del HTML, clasifica el **sector** (oeste/noroeste/este/sur) y calcula la **distancia (km) a la zona de actividades** (ancla Granada–El Peñón). El método se validó contra el feedback del usuario (acertó: Casa 4 Hab→este ~5 km, Apto moderno→sur ~11 km, Casa Bella→oeste ~1 km). Se agregó una **columna de distancia** en los 4 entregables.
  - **Rebarrido del noroeste** (Granada, Santa Mónica, Versalles, Centenario, El Peñón, Santa Teresita, Vipasa). **Hallazgo honesto:** casas/aptos enteros para 7, en el oeste core, disponibles y en presupuesto, hay **muy pocos**.
  - **Nuevo ranking (3 que cumplen):** 1º *Apartamento cerca del Estadio* (oeste ~1,9 km, 5 camas, 2 baños, **79.2**), 2º *Casa 7p con garaje* (centro-oeste ~3,6 km, **78.4**), 3º *Espacioso refugio Vistas* (oeste ~2,4 km, 3 baños, **63.2**, flex). Mejor + carro local ≈ **$286.407 pp (DENTRO)**.
  - **Límite reconocido:** la **disponibilidad para la noche del 30 no se puede auto-verificar** fiable desde el scrape (el calendario por-noche no se expone) — se marca "confirmar al reservar" con el link directo. Las amenidades (aire/piscina) siguen "según el anuncio" (su detección varía entre corridas). El `corto`/distancia y las coordenadas quedan como la señal dura.

- **Actualización v4 (2026-10-04) — ampliar opciones + disponibilidad del rango completo:** el usuario reportó que el Apto cerca Estadio tiene el problema inverso (no permite la **salida el 2**) y pidió **más opciones**. Se decidió:
  - **Intento de leer el calendario** (3 noches: 30, 31, 1) desde el HTML de la ficha → **no sirve**: Airbnb carga el calendario por una llamada aparte (quedó en "?"). Confirmado: la disponibilidad hay que verificarla manualmente en el link; las notas pasaron a decir **rango 30→2** (no solo el 30).
  - **Barrido ampliado a 10 barrios** del noroeste (+ Normandía, La Flora, Prados del Norte, San Antonio). **Realidad confirmada:** el inventario de casas/aptos enteros para 7 en Cali es finito (~24 únicos en presupuesto; se repiten entre búsquedas), la mayoría al este/sur, con <5 camas o fuera de presupuesto.
  - **Set ampliado a 4 que cumplen** (cap 7 + camas ≥5 + noroeste/oeste + presupuesto), verificadas por coordenadas: 1º *Agradable y Hermoso Apto (La Flora)* (**7 camas**, aire, 5,0★, pero norte ~4,8 km, **72.4**), 2º *Casa 7p garaje* (~3,6 km, **70.8**), 3º *Casa-museo Fundación Cerón* (la más cerca, ~0,6 km en San Antonio, **65.3**), 4º *Refugio Vistas* (~2,4 km, **63.2**). Se explicita en el informe el trade-off puntaje-vs-distancia (la #1 es la más cómoda pero la más lejos; la más céntrica es la casa-museo).
  - **Descartes transparentes** (con coordenadas): Apto Granada/Chipichape y Torre Gardes (noroeste pero 4 camas), Casa Bella (sin dispo el 30), Apto cerca Estadio (sin salida el 2), Casa piscina (fuera de presupuesto).
  - **Gráfico:** eje fijado a **0–100** (`value_axis.minimum/maximum_scale`) para no exagerar diferencias cuando los puntajes están agrupados.

- **Actualización v5 (2026-10-04) — el usuario descartó 2 por calidad/disponibilidad:** *Casa 7p garaje* (fea) y *Refugio Vistas* (noches no disponibles + cara) salieron a `AIRBNB_DESCARTES` con su razón. Se promovieron las dos mejores del noroeste que quedaban: *Apto Granada/Chipichape* (~1,8 km, la más céntrica/barata) y *Torre Gardes* (~3 km, piscina, 4 baños, 5,0★). **Nuevo set de 4** (La Flora, Casa-museo, + las dos nuevas). Dos decisiones de método:
  - **La ★ ya no es automáticamente la de mayor puntaje**, sino la mejor **con cama para los siete** (`camas >= personas-2 = 5`): `AIRBNB_MEJOR = max(camas>=5, key=puntaje)`. Las dos nuevas traen **4 camas** (capacidad 8 con sofá-cama) y, aunque *Apto Granada/Chipichape* encabeza el puntaje (77.2, por barata y céntrica), la ★ y el paquete "Casa entera" apuntan a **La Flora** (7 camas). Se explica el matiz en informe, PDF y en la tarjeta del gráfico (la barra resaltada no es la más alta — es la práctica para dormir a 7).
  - **Normalización de precio:** se mantuvo *dentro del set* pero el set tiene 4 (no 2) justo para que la normalización no se distorsione (con 2 precios casi iguales, uno caía a 5 y otro a 1 — artefacto). Lección: el ranking relativo necesita ≥3–4 ítems para que el sub-puntaje de precio sea informativo.
  - **Inventario:** confirmado agotado para el criterio estricto — en el noroeste/oeste cerca de actividades, con 7 personas y presupuesto, las opciones con camas ≥5 son contadas; las demás (Casa Bella, Apto Estadio) caen por disponibilidad.

- **Actualización v6 (2026-10-04) — verificación DURA de disponibilidad y tipo de propiedad:** el usuario (molesto, con razón) tuvo que cazar a mano que las opciones fallaban por disponibilidad por-noche y por tipo. Se corrigió de raíz:
  - **Nuevo `src/scrapers/verifica_airbnb.py`:** intercepta la llamada real de Airbnb `PdpAvailabilityCalendar` (disponibilidad por día: available / forCheckin / forCheckout / minNights) y decide el rango exacto **30→2** de verdad; y lee la **página /amenities** (sin ruido de "similares") para el aire. Validado contra el feedback: Torre Gardes/Casa Bella/Apto Estadio → NO; La Flora/Casa-museo → DISPONIBLE. El calendario embebido en HTML NO servía (carga aparte); la intercepción de red SÍ.
  - **Tipo de propiedad por `sharingConfig`:** varias "casas" eran en realidad **apartahotel/hotel** (Lofthouse 14) o **habitación compartida con baños compartidos** (viola el requisito base). Se extrae `propertyType` + overview autoritativo del HTML. Lección: **nunca asumir "casa entera" por el título** — Airbnb mezcla apartahoteles, hoteles y habitaciones compartidas en los resultados aunque filtres.
  - **Bug propio:** una alternancia de regex sin agrupar (`(\d+)\s+a|b`) devolvía `group(1)=None` → `int(None)`. Agrupar con `(?:...)`.
  - **Set final = 3 casas ENTERAS con rango 30→2 verificado:** La Flora (7 camas, aire, 5,0, ~4,8 km, **80.1** ★), Casa-museo (6 camas, ~0,6 km la más céntrica, 73.2), Apto entero con servicios (hallazgo del usuario; 4 camas, 4 baños, aire, ~3,6 km, 66.8). Descartes marcados por tipo/disponibilidad (apartahotel, hotel, habitación compartida, sin fechas).
  - **Pedido del usuario atendido:** se agregó la columna **Total (3 noches)** junto a la de por-persona en los 4 entregables.

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
