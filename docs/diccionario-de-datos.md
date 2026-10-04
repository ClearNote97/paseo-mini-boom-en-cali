# 📖 Diccionario de datos

> Describe **qué significa cada variable** de los datos del proyecto: nombre, tipo, significado, dominio y origen.
> Se organiza **un bloque por dataset** (archivo o tabla) y se llena a medida que se incorporan datos.
>
> **Cómo se usa:** por cada dataset, una breve descripción + una tabla de variables. Copia la plantilla del
> final para agregar un dataset nuevo. Los tipos se escriben en lenguaje llano (`entero`, `decimal`,
> `texto`, `fecha`, `booleano`, `categórico`), no en el tipo interno de pandas.

---

## `estadia_opciones` — `data/other/estadia_opciones.csv`

_Cada fila es **una opción de alojamiento** candidata para el viaje a Cali (7 personas, 3 noches: 30 oct – 2 nov 2026).
Recolectada de plataformas de reserva y enriquecida con una señal de seguridad del barrio. Granularidad: una fila = un
alojamiento en una plataforma (el mismo alojamiento en dos plataformas = dos filas, se deduplica luego)._

| Variable | Tipo | Descripción | Dominio / valores | Fuente |
|---|---|---|---|---|
| `id` | entero | Identificador único de la opción | `> 0`, único | generado |
| `nombre` | texto | Nombre del alojamiento | — | plataforma |
| `plataforma` | categórico | Dónde se encontró | `booking`, `airbnb`, `hostelworld`, `otro` | plataforma |
| `tipo` | categórico | Arquetipo de alojamiento | `casa_entera`, `apto_entero`, `dorm_privado`, `habs_privadas`, `hostal` | plataforma |
| `barrio` | texto | Barrio / zona de Cali | ej. `Granada`, `San Antonio`, `El Peñón`, `Santa Teresita` | plataforma |
| `lat` | decimal | Latitud | — | plataforma |
| `lng` | decimal | Longitud | — | plataforma |
| `capacidad_max` | entero | Personas que admite | `>= 7` (filtro duro) | plataforma |
| `num_camas` | entero | Camas disponibles (comparten cama sin abusar) | `>= 5` (**filtro duro**) | plataforma |
| `num_habitaciones` | entero | Número de habitaciones | `>= 1` | plataforma |
| `num_banos` | entero | Número de baños | `>= 1` | plataforma |
| `precio_total_3noches` | decimal | Precio total por las 3 noches, grupo completo | `>= 0` (COP) | plataforma |
| `precio_por_persona` | decimal | `precio_total_3noches / 7` | `>= 0` (COP) | calculado |
| `aire_acondicionado` | booleano | Tiene AC (valorado positivamente — Cali es cálida) | `true` / `false` | plataforma |
| `amenidades` | texto | Lista separada por `;` | de: `cocina`, `piscina`, `terraza`, `zonas_comunes`, `bar`, `wifi`, `agua_caliente`, `lavadora`, `desayuno`, `parqueadero` | plataforma |
| `cerca_rumba` | booleano | A pie de vida nocturna (Granada/Menga/El Peñón) | `true` / `false` | derivado |
| `tiene_parqueadero` | booleano | Parqueadero para el carro alquilado | `true` / `false` | plataforma |
| `distancia_zona_turistica_km` | decimal | Distancia al centro de la zona turística (Oeste) | `>= 0` | calculado |
| `rating` | decimal | Calificación de la plataforma | `0`–`10` (normalizado) | plataforma |
| `num_resenas` | entero | Número de reseñas | `>= 0` | plataforma |
| `senal_seguridad` | entero | Señal de seguridad del barrio (1 peor – 5 mejor) | `1`–`5` | reseñas + contexto |
| `puntaje_total` | decimal | Puntaje ponderado (ver marco de puntuación en `D-001`) | `0`–`100` | calculado |
| `url` | texto | Enlace a la opción | — | plataforma |
| `fecha_consulta` | fecha (`YYYY-MM-DD`) | Cuándo se consultó el precio | — | generado |

**Filtros duros (pasa/no pasa) antes de puntuar:** `capacidad_max >= 7` · `num_camas >= 5` · disponible 30 oct–2 nov 2026 · `senal_seguridad >= 3` (barrio aceptable) · `precio_por_persona <= 480000` (techo con flex del +20%).

---

## `transporte_opciones` — `data/other/transporte_opciones.csv`

_Cada fila es **una opción de movilización local** para los 4 días (recogida en el aeropuerto Palmaseca). Incluye
alquiler de vehículo (van o carro) y, como comparación, alternativas por viaje (Uber/DiDi/taxi estimado sobre el itinerario)._

| Variable | Tipo | Descripción | Dominio / valores | Fuente |
|---|---|---|---|---|
| `id` | entero | Identificador único | `> 0`, único | generado |
| `modo` | categórico | Tipo de solución | `alquiler`, `uber_didi`, `taxi` | — |
| `agencia` | texto | Agencia o servicio | ej. `Localiza`, `Hertz`, `Avis`, `Alamo`, local | plataforma |
| `categoria_vehiculo` | categórico | Categoría del vehículo | `van`, `suv`, `sedan`, `2_carros` | plataforma |
| `capacidad_pax` | entero | Pasajeros | `>= 7` (filtro duro para alquiler) | plataforma |
| `capacidad_maletas` | entero | Maletas grandes que caben | `>= 0` | plataforma |
| `precio_dia` | decimal | Tarifa por día | `>= 0` (COP) | plataforma |
| `precio_total_4dias` | decimal | Tarifa × 4 días | `>= 0` (COP) | calculado |
| `seguro_incluido` | booleano | Seguro/cobertura incluido en tarifa | `true` / `false` | plataforma |
| `deposito` | decimal | Depósito retenido en tarjeta | `>= 0` (COP) | plataforma |
| `recogida_aeropuerto` | booleano | Entrega en aeropuerto Palmaseca | `true` / `false` | plataforma |
| `gasolina_estimada` | decimal | Combustible estimado los 4 días | `>= 0` (COP) | estimado |
| `parqueadero_estimado` | decimal | Parqueadero estimado (si el alojamiento no tiene) | `>= 0` (COP) | estimado |
| `costo_total_estimado` | decimal | Suma: tarifa + gasolina + parqueadero | `>= 0` (COP) | calculado |
| `costo_por_persona` | decimal | `costo_total_estimado / 7` | `>= 0` (COP) | calculado |
| `rating_agencia` | decimal | Reputación de la agencia | `0`–`5` | reseñas |
| `puntaje_total` | decimal | Puntaje ponderado (ver `D-001`) | `0`–`100` | calculado |
| `url` | texto | Enlace | — | plataforma |
| `fecha_consulta` | fecha (`YYYY-MM-DD`) | Cuándo se consultó | — | generado |

---

## `paquetes` — `output/paquetes.csv`

_Entregable final: **2–3 paquetes armados** cruzando una estadía + una opción de transporte, con el costo por persona
validado contra el presupuesto. Cada fila es un paquete propuesto._

| Variable | Tipo | Descripción | Dominio / valores | Fuente |
|---|---|---|---|---|
| `paquete` | categórico | Arquetipo | `hostal_social`, `casa_entera`, `economico` | armado |
| `estadia_id` | entero | FK a `estadia_opciones.id` | — | armado |
| `transporte_id` | entero | FK a `transporte_opciones.id` | — | armado |
| `costo_estadia_pp` | decimal | Costo estadía por persona | `>= 0` (COP) | calculado |
| `costo_transporte_pp` | decimal | Costo transporte por persona | `>= 0` (COP) | calculado |
| `costo_total_pp` | decimal | Total por persona (meta 300–400k, techo 480k) | `>= 0` (COP) | calculado |
| `dentro_presupuesto` | categórico | Ubicación vs presupuesto | `dentro`, `flex`, `excede` | calculado |
| `notas` | texto | Justificación del paquete (amenidades, seguridad, trade-off) | — | armado |

---

## `AIRBNB_ENTEROS` — `src/generar_entregables.py` (barrido Airbnb, ver `D-005`)

_Cada fila es **una casa o apartamento entero** de Airbnb candidato para los 7 (3 noches, 30 oct–2 nov 2026),
recolectado con Playwright (`src/scrapers/explora_airbnb.py` + `explora_fichas_airbnb.py`). Lo distintivo frente a
`estadia_opciones`: al ser alojamiento **completo**, **ningún baño se comparte con extraños**. La data curada vive en
el código (fuente única); los `*.json` del scraper son artefactos intermedios no versionados._

| Variable | Tipo | Descripción | Dominio / valores | Fuente |
|---|---|---|---|---|
| `nombre` | texto | Título del anuncio | — | Airbnb |
| `corto` | texto | Etiqueta corta (para el gráfico de barras) | — | armado |
| `zona` | texto | Barrio / zona de Cali | ej. `San Antonio`, `Granada` | Airbnb |
| `cap` | entero | Huéspedes que admite | `>= 7` | ficha |
| `hab` | entero | Habitaciones | `>= 1` | ficha |
| `camas` | entero | Camas | `>= 5` (los que no cumplen van a `AIRBNB_DESCARTES`) | ficha |
| `banos` | decimal | Baños (puede ser `.5` = medio baño); **todos del grupo** | `>= 1` | ficha |
| `total` | entero | Precio total del periodo (3 noches), alojamiento completo | `>= 0` (COP) | Airbnb |
| `pp` | entero | `total // 7` — por persona (3 noches) | `>= 0` (COP) | calculado |
| `ac` | booleano | Aire acondicionado (según el anuncio) | `true` / `false` | ficha |
| `piscina` | booleano | Piscina (según el anuncio) | `true` / `false` | ficha |
| `cocina` | booleano | Cocina | `true` (alojamiento entero) | ficha |
| `seguridad` | entero | Señal de seguridad del barrio (1–5) | `1`–`5` | zona + contexto |
| `cercania` | entero | Cercanía a la zona de actividades (1–5) | `1`–`5` | zona |
| `parq` | entero | Parqueadero/garaje (1–5) | `1`–`5` | ficha |
| `social` | entero | Ambiente social (1–5; una casa entera es baja por diseño) | `1`–`5` | armado |
| `rating` | decimal | Calificación de Airbnb | `0`–`5` | Airbnb |
| `reco` | booleano | La mejor por puntaje (★); se calcula, no se fija a mano | `true` / `false` | calculado |
| `link` | texto | Enlace al anuncio (`/rooms/<id>`) | — | Airbnb |
| `nota` | texto | Comentario (por qué entra / trade-off) | — | armado |

> **Mismo puntaje que los hostales, ranking SEPARADO (ver `D-005` v2):** `puntaje_ab()` aplica los mismos pesos
> (`PESOS_ESTADIA`: seguridad 30 · amenidades 20 · precio 20 · cercanía 12 · parqueadero 10 · social 8), con el
> **precio normalizado dentro del set Airbnb** (`_sub_precio_ab`). No se mezcla con el ranking de hostales (que queda
> intacto). `AIRBNB_RANK` ordena por puntaje; `AIRBNB_MEJOR` es el primero.

> **Dimensión de baños (informativa, no puntúa):** en la tabla de estadía está la columna **"¿Baño compartido?"**
> (`bano_compartido()`): `No` para casa/apto entero, `Depende*` para hostal. No es filtro ni peso — informa al grupo.

**Amenidades "según el anuncio":** `ac` y `piscina` salen de la sección de amenidades de la ficha (tras recortar el
carrusel de "similares" que contaminaba la detección). Se muestran como "Sí/—" con la advertencia de confirmar al
reservar. Honestidad > falso dato.

---

<!-- ─────────────────────────────────────────────────────────────────────────────
PLANTILLA PARA UN NUEVO DATASET (copia este bloque y quítale el comentario)

## `<nombre_del_dataset>` — `ruta/al/archivo`

_Breve descripción del dataset._

| Variable | Tipo | Descripción | Dominio / valores | Fuente |
|---|---|---|---|---|
| `<variable>` | <tipo> | <qué es> | <valores posibles> | <origen> |

───────────────────────────────────────────────────────────────────────────── -->
