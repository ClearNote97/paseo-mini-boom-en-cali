# Mini-Boom en Cali
### Dossier de logística · transporte y estadía para siete

![Cartagena](./assets/flag_cartagena.png) → ![Cali](./assets/flag_cali.png)  
*De Cartagena a Cali.*

*Informe completo · 1 de octubre de 2026 · **planeación v2** (ajustada al nuevo horario de vuelo). Lo acompañan un [resumen ejecutivo](./Mini-Boom-en-Cali_Resumen-ejecutivo.pdf), una [hoja de cálculo](./Mini-Boom-en-Cali_Resultados.xlsx) y una [presentación](./Mini-Boom-en-Cali_Presentacion.pptx).*

---

## Índice

1. [Punto de partida](#punto-de-partida)
2. [Cómo se hizo esto](#cómo-se-hizo-esto)
3. [Geografía de la seguridad](#geografía-de-la-seguridad)
4. [Estadía: el puntaje y los finalistas](#estadía-el-puntaje-y-los-finalistas)
5. [Movilidad: la llegada es de noche](#movilidad-la-llegada-es-de-noche)
6. [Movilidad: las tres opciones](#movilidad-las-tres-opciones)
7. [Cuatro lecturas del presupuesto](#cuatro-lecturas-del-presupuesto)
8. [La recomendación](#la-recomendación)
9. [Lo que queda por confirmar](#lo-que-queda-por-confirmar)

---

## Punto de partida

Siete personas, tres noches, una ciudad que premia al que planea. Del viernes 30 de octubre al lunes 2 de noviembre de 2026 —fin de semana de Halloween, con Cali en su punto más salsero y más lleno—. El vuelo de ida sale de Cartagena a las 6 de la tarde y **aterriza a las 8 de la noche del 30**; el regreso es en el vuelo de las 9 de la noche del 2. La pregunta no es cómo llegar, sino cómo movernos por la ciudad y dónde dormir sin que el presupuesto ni la seguridad cedan.

El margen es explícito: **$300.000 a $400.000 por persona** entre transporte y estadía, con licencia de estirar hasta **$480.000** cuando la calidad lo amerite. Y una condición innegociable: la seguridad va primero. Después, lo que hace memorable un viaje —piscina para el calor, aire para la noche, cocina para no dejar el sueldo en restaurantes, y la rumba a pie.

> **Nota de la v2:** el cambio de horario de la ida (antes llegábamos de mañana) no toca la estadía; reordena solo la movilidad —para mejor en costo y con un cuidado nuevo por la llegada nocturna—.

## Cómo se hizo esto

Esto se armó como un pequeño proyecto de datos, no a ojo. El orden importa:

1. **Primero la vara, después la búsqueda.** Se fijaron los pesos de cada criterio —con la seguridad mandando— antes de mirar un solo precio.
2. **Precios reales, no de folleto.** Un navegador automatizado (Playwright) recorrió Hostelworld con las fechas exactas y siete huéspedes; el transporte se cotizó contra Kayak y agencias locales de Cali.
3. **Un puntaje propio y auditable** para la estadía (se explica abajo), separado de la calificación de huéspedes de las plataformas.
4. **Una sola fuente de datos** genera estos cuatro documentos: si un número cambia, los cuatro se actualizan en coherencia.

## Geografía de la seguridad

Cali se lee por barrios. Donde el viajero duerme tranquilo y amanece cerca de todo: **San Antonio, Granada, El Peñón, Santa Teresita, Ciudad Jardín**. San Antonio —casas de colores, cuestas empedradas, salsa en cada esquina— es el favorito por razón. Lo que conviene esquivar: **Aguablanca (oriente), Siloé, Terrón Colorado (ladera oeste alta)**; la última es la subida al oeste alto, y suele ofrecerse disfrazada de ganga con vista.

## Estadía: el puntaje y los finalistas

El **9.6 o 9.8** junto a cada hostal es la calificación de huéspedes de Hostelworld, un dato externo. La decisión no se apoyó en ese número: se construyó un puntaje propio, de 0 a 100, con una nota de 1 a 5 por criterio multiplicada por su peso.

| Criterio | Peso | Cómo se asigna la nota (1–5) |
|---|:--:|---|
| 🔒 Seguridad del barrio | 30% | Por zona (San Antonio / Granada / El Peñón = 5) |
| ✨ Amenidades y comodidad | 20% | Aire acondicionado +2, piscina +2, cocina +1 (tope 5) |
| 💰 Precio por persona | 20% | El más barato = 5; escala lineal hasta el más caro = 1 |
| 📍 Cercanía a zona turística | 12% | Qué tan a pie queda de lo turístico |
| 🅿️ Parqueadero | 10% | Disponibilidad estimada *(baja certeza)* |
| 🎉 Ambiente social | 8% | Facilidad para conocer gente |

> **Fórmula:** puntaje = suma de (peso × nota⁄5). Con el líder, Viajero Hostel & Salsa School: 30×5⁄5 + 20×4⁄5 + 20×1.9⁄5 + 12×5⁄5 + 10×2⁄5 + 8×5⁄5 = **77.6/100**.

Ordenados por ese puntaje propio. La última columna es para juzgar con ojos propios:

| # | Hostal | Zona | Puntaje | Calificación huéspedes | Aire | Piscina | ¿Baño compartido? | Estadía por persona (3 noches) | Ver |
|:--:|---|---|:--:|:--:|:--:|:--:|:--:|--:|:--:|
| 1 | Viajero Hostel & Salsa School ★ | San Antonio | **77.6** | 9.6 | ✔ | ✔ | Depende* | $252.282 | [link](https://www.hostelworld.com/hostels/p/73676/viajero-cali-hostel-and-salsa-school/) |
| 2 | La Palmera Hostel | San Antonio | **75.8** | 9.7 | — | ✔ | Depende* | $150.000 | [link](https://www.hostelworld.com/hostels/p/314482/la-palmera-hostel/) |
| 3 | Oasis Cali Hostel | Granada | **75.4** | 9.6 | ✔ | — | Depende* | $150.000 | [link](https://www.hostelworld.com/hostels/p/284050/oasis-cali-hostel/) |
| 4 | La Chanca Hostel | San Antonio | **74.8** | 9.8 | — | — | Depende* | $89.850 | [link](https://www.hostelworld.com/hostels/p/329092/la-chanca-hostel/) |
| 5 | Hostal Patio del Río | Oeste (Cali) | **72.8** | 9.6 | ✔ | ✔ | Depende* | $189.750 | [link](https://www.hostelworld.com/hostels/p/323610/hostal-patio-del-rio/) |
| 6 | Casa/Apto entero (Airbnb) | San Antonio (Oeste) | **71.2** | — | ✔ | ✔ | No | $300.000 | [link](https://www.airbnb.com/s/San-Antonio--Cali--Valle-del-Cauca/homes?checkin=2026-10-30&checkout=2026-11-02&adults=7) |

- **[Viajero Hostel & Salsa School](https://www.hostelworld.com/hostels/p/73676/viajero-cali-hostel-and-salsa-school/)** — AC, piscina, bar, clases de salsa gratis, desayuno. El más completo en amenidades y ambiente.
- **[La Palmera Hostel](https://www.hostelworld.com/hostels/p/314482/la-palmera-hostel/)** — Privadas con ventilador (no AC) y balcón con vista. Clases de salsa. Rating 9.7.
- **[Oasis Cali Hostel](https://www.hostelworld.com/hostels/p/284050/oasis-cali-hostel/)** — En Granada, zona gastronómica y segura. Clases de salsa, tours, desayuno.
- **[La Chanca Hostel](https://www.hostelworld.com/hostels/p/329092/la-chanca-hostel/)** — El mejor rating del barrido (9.8) y el más económico. Amenidades básicas con cocina.
- **[Hostal Patio del Río](https://www.hostelworld.com/hostels/p/323610/hostal-patio-del-rio/)** — Piscina y AC. Equilibrio entre amenidades y precio, dentro de la meta.
- **[Casa/Apto entero (Airbnb)](https://www.airbnb.com/s/San-Antonio--Cali--Valle-del-Cauca/homes?checkin=2026-10-30&checkout=2026-11-02&adults=7)** — Casa entera de 4 habitaciones con piscina, AC y cocina. Máxima privacidad; estimado ~300k por persona (3 noches).

> **\* Sobre los baños:** el grupo no quiere compartir baño con extraños. En un hostal eso *depende de la habitación* — hay que confirmar al reservar que tenga baño propio (o reservar una habitación privada para los siete). La casa o apto entero resuelve el punto de raíz: **ningún baño se comparte**. Es una dimensión informativa; **no entra al puntaje** (lo decide el grupo).

### Airbnb — casas y aptos enteros en el occidente (mismo puntaje, ranking aparte)

El grupo pidió apuntar al **occidente de Cali, cerca de la zona de actividades** (San Antonio, El Peñón, Granada, Santa Teresita), y en casa o apartamento **entero** — donde ningún baño se comparte con extraños. Se rebuscó con Playwright y se les aplicó **el mismo puntaje 0–100** que a los hostales (seguridad 30% · amenidades 20% · precio 20% · cercanía 12% · parqueadero 10% · social 8%), en un **ranking separado**: aquí el precio se normaliza entre las casas, y el ambiente *social* las castiga (no hay bar ni vida de hostal) — por eso se comparan entre ellas, no contra los hostales.

> **Lectura rápida:** la mejor por puntaje es **Casa amoblada para 7 personas con garaje** (94.6/100). Hay casas enteras desde ~$78.571 por persona las 3 noches, así que la opción privada es, además, de las más económicas. *Aire y piscina van «según el anuncio» — confirmar al reservar.*

| # | Casa / apto entero | Zona | Puntaje | Cabe | Camas | Baños | Aire | Piscina | ★ Rating | Por persona (3n) | Ver |
|:--:|---|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|--:|:--:|
| 1 | **Casa amoblada para 7 personas con garaje** ★ | San Antonio | **94.6** | 7 | 5 | 2,5 | Sí | Sí | 4.97 | $90.714 | [link](https://www.airbnb.com/rooms/38526055) |
| 2 | **Casa Bella, espaciosa en la bohemia San Antonio** | San Antonio | **89.7** | 8 | 5 | 2 | Sí | Sí | 4.92 | $156.186 | [link](https://www.airbnb.com/rooms/49321247) |
| 3 | **Casa de 4 Habitaciones – Terraza y Aire/C** | San Antonio | **89.2** | 9 | 5 | 1,5 | Sí | Sí | 4.89 | $78.571 | [link](https://www.airbnb.com/rooms/1048602132521468133) |
| 4 | **Apartamento moderno con piscina** | Granada | **80.9** | 8 | 5 | 2 | — | Sí | 4.86 | $172.576 | [link](https://www.airbnb.com/rooms/1699978286025248131) |
| 5 | **Casa Amplia y Cómoda en Las Flores** | Las Flores (norte) | **76.1** | 8 | 6 | 2 | Sí | — | 4.96 | $94.285 | [link](https://www.airbnb.com/rooms/1071190715409487725) |
| 6 | **Casa para 8 personas** | Granada | **71.1** | 9 | 6 | 2 | — | — | 4.96 | $124.151 | [link](https://www.airbnb.com/rooms/880582897050465656) |
| 7 | **Casa con piscina privada** | San Antonio | **66.8** | 8 | 5 | 2,5 | — | Sí | 4.97 | $430.608 | [link](https://www.airbnb.com/rooms/825481159079037573) |

**Mejor casa por puntaje (Casa amoblada para 7 personas con garaje, 94.6/100) + carro propio local ≈ $290.714 por persona** (dentro): baños del grupo, cocina y privacidad total. El trade-off frente al hostal sigue siendo el ambiente social; San Antonio pone la rumba a pie de todos modos.

Dos que se ven baratas pero **no cumplen** (por eso se miran baños y camas, no solo el precio):

- **[Apto familiar – ubicación estratégica](https://www.airbnb.com/rooms/1538036648539244464)** (Granada, $104.062 pp · 4 camas · 2 baños) — Barato y céntrico, pero solo 4 camas (bajo el mínimo de 5 para los siete).
- **[Apto grande y tranquilo](https://www.airbnb.com/rooms/934280562272881551)** (San Fernando, $111.951 pp · 3 camas · 1 baño) — Dice 16 huéspedes pero trae 3 camas y 1 solo baño: ni camas ni baños para el grupo.
- **[L2 – San Antonio (balcón)](https://www.airbnb.com/rooms/1590016903260349041)** (San Antonio, $220.285 pp · 3 camas · 1 baño) — Buena zona, pero 3 camas, 1 baño y caro: no compensa.

## Movilidad: la llegada es de noche

La llegada es a las 8 de la noche del 30, un viernes. El viaje entra en tres días de alquiler limpios (se recoge esa noche y se devuelve ~7 pm del 2, por debajo de las 72 horas). Para la hora, lo que mejor cuadra es una agencia local (Farallones, WayCarCali) que entrega el carro coordinando el vuelo. Los mostradores del aeropuerto (Alamo/Localiza) salen más baratos pero cierran ~10 pm, así que si se recoge ahí conviene reservar la recogida fuera de horario (24 h de aviso) por si el vuelo se retrasa. Y como red: los taxis oficiales del aeropuerto operan 24/7 (distintivo amarillo, tarifados, seguros).

El alquiler se cuenta por días de 24 horas desde la recogida, con una hora de gracia; con la llegada de noche, los tres días cuadran hasta la tarde del 2. El matiz, corregido: el mostrador del aeropuerto sale un poco más barato pero tiene horario rígido (cierra ~10 pm); una agencia local cuesta algo más y, a cambio, entrega coordinando el vuelo — que es lo que de verdad cuadra con una llegada a las 8 pm.

## Movilidad: las tres opciones

Como quieren salir de Cali con libertad, el carro propio tiene sentido. Aun así, estas son las tres formas de resolverlo, de la más cómoda a la más barata. Todas con costo todo-incluido por persona (grupo de 7, con gasolina y taxis donde aplican); la cifra dura de referencia es el 7 puestos de Kayak en el aeropuerto (3 días).

| Opción | Qué implica | Por persona | Comodidad | Ver |
|---|---|--:|---|:--:|
| **Carro propio entregado por una agencia local (cuadra con la llegada de noche)** ★ | Una agencia local (Farallones, WayCarCali) entrega el carro coordinando el vuelo, sin pelear con el horario del mostrador; ~3 días con gasolina. P. ej. la Captiva Turbo (~$1.200.000 / 3 días). | **$200.000** | La más libre y la que cuadra con la llegada de noche; cuesta un poco más que el mostrador. | [ver](https://farallonesrentacar.com/listavehiculos/) |
| **Carro propio en el mostrador del aeropuerto (Kayak)** | Más barato (p. ej. Nissan X-Trail $1.033.028 / 3 días), pero el mostrador (Alamo/Localiza) cierra ~10 pm: con la llegada 8 pm va apretado, y si el vuelo se retrasa hay que reservar recogida fuera de horario (24 h de aviso). | **$180.000** | El carro más barato, pero el horario del mostrador aprieta con la llegada de noche. | [ver](https://www.kayak.com.co/cars/Santiago-de-Cali,Colombia-c11092/2026-10-30/2026-11-02;map?fs=carcapacity=precise_7;carlocationid=~CLO&ucs=9x1xcq&sort=rank_a) |
| **Sin carro propio: taxis y una van con conductor para el paseo de afuera** | Taxi oficial de llegada (24/7), Uber/DiDi en la ciudad y una van con conductor contratada solo el día que salgan de Cali. | **$125.000** | La más barata y sin manejar ni parquear; menos ideal si quieren varias salidas de la ciudad. | [ver](https://carrent.com.co/alquiler-de-van-en-cali) |

> La diferencia clave no es tanto el precio como el horario: el mostrador del aeropuerto es un poco más barato pero cierra ~10 pm; una agencia local cuesta algo más y entrega coordinando el vuelo, que es lo que cuadra con la llegada de las 8 pm. Los totales de 3 días de las locales se cierran por WhatsApp.

**Vehículos de 7 puestos para las fechas** — lo que cambia según dónde se recoja (local vs mostrador):

| Vehículo (7 puestos) | Agencia | Tarifa (3 días) | Por persona | ¿Cuadra con la llegada? | Ver |
|---|---|---|--:|---|:--:|
| Chevrolet Captiva Turbo | Farallones (local) | ~$1.200.000 | $171.429 | Sí — oficina en el aeropuerto y domicilio | [ver](https://farallonesrentacar.com/car-model/captiva-turbo-7-puestos/) |
| Toyota Fortuner | Farallones (local) | desde $1.140.000 | $162.857 | Sí — entrega coordinando el vuelo | [ver](https://farallonesrentacar.com/listavehiculos/) |
| Mitsubishi Montero Sport | Farallones (local) | desde $705.000 | $100.714 | Sí — entrega coordinando el vuelo | [ver](https://farallonesrentacar.com/listavehiculos/) |
| 7 puestos (varios modelos) | WayCarCali (local) | desde $360.000 | $51.429 | Sí — domicilio gratis al aeropuerto (3+ días) | [ver](https://waycarcali.com/) |
| Nissan X-Trail | Kayak · EconomyBookings | $1.033.028 | $147.575 | Mostrador: cierra ~10 pm | [ver](https://www.kayak.com.co/cars/Santiago-de-Cali,Colombia-c11092/2026-10-30/2026-11-02;map?fs=carcapacity=precise_7;carlocationid=~CLO&ucs=9x1xcq&sort=rank_a) |
| SUV mediano híbrido | Kayak · Alkilautos | $1.847.639 | $263.948 | Mostrador: cierra ~10 pm | [ver](https://www.kayak.com.co/cars/Santiago-de-Cali,Colombia-c11092/2026-10-30/2026-11-02;map?fs=carcapacity=precise_7;carlocationid=~CLO&ucs=9x1xcq&sort=rank_a) |

> Todos los precios son por los 3 días, solo el alquiler (sin gasolina ni parqueo). Las tarifas locales 'desde' se calculan sobre la tarifa base/día × 3; en alquiler corto el total real suele ser mayor (la Captiva, confirmada, cuesta ~$1.200.000) — pidan el exacto por WhatsApp. Lo clave sigue siendo el horario: las locales entregan coordinando el vuelo; los mostradores cierran ~10 pm.

**Cómo cambia el total** con el hostal recomendado (Viajero, $252.282 por persona de estadía):

| Estadía + forma de moverse | Total por persona | En el bolsillo |
|---|--:|:--:|
| Viajero + sin carro propio | **$377.282** | DENTRO |
| Viajero + carro mostrador (kayak) | **$432.282** | FLEX |
| Viajero + carro local (entrega) ★ | **$452.282** | FLEX |

## Cuatro lecturas del presupuesto

Cada lectura combina un hostal con la movilidad recomendada (carro local (entrega), $200.000 por persona). Con otra forma de moverse, el total se corre según la tabla de arriba.

| Lectura | Estadía | Total por persona | En el bolsillo |
|---|---|--:|:--:|
| **Económico** | [La Chanca Hostel](https://www.hostelworld.com/hostels/p/329092/la-chanca-hostel/) | **$289.850** | DENTRO |
| **Amenidades en meta** | [Hostal Patio del Río](https://www.hostelworld.com/hostels/p/323610/hostal-patio-del-rio/) | **$389.750** | DENTRO |
| **El equilibrio** ★ | [Viajero Hostel & Salsa School](https://www.hostelworld.com/hostels/p/73676/viajero-cali-hostel-and-salsa-school/) | **$452.282** | FLEX |
| **Casa entera** | [Casa amoblada para 7 personas con garaje](https://www.airbnb.com/rooms/38526055) | **$290.714** | DENTRO |

## La recomendación

**Viajero Hostel & Salsa School (estadía) + carro propio entregado por una agencia local ≈ $452.282 por persona.** El hostal responde que sí a cada exigencia a la vez —zona más segura y caminable, piscina, aire, bar y rumba a un costado, y las clases de salsa que resuelven eso de conocer gente—. Y el carro, con una agencia local (Farallones, WayCarCali) que lo entrega coordinando el vuelo, da la libertad que pidieron para salir de Cali **sin pelear con el horario del mostrador**.

Palancas según la prioridad: el **mostrador del aeropuerto** (Kayak) es algo más barato ($432.282) pero cierra ~10 pm y aprieta con la llegada de noche; moverse **sin carro propio** baja a $377.282 (entra en meta), a cambio de menos libertad para las salidas de la ciudad.

## Lo que queda por confirmar

Las cartas boca arriba:

- **Estadía:** ¿el precio es por persona o por habitación? Se asumió por persona (lo prudente). Y confirmar capacidad para siete con camas mínimo cinco al abrir cada ficha. En Airbnb los totales son del alojamiento completo (ya divididos entre 7) pero faltan las **tarifas de servicio/limpieza**; en hostal, confirmar que la habitación tenga **baño propio** para no compartirlo con extraños.
- **Carro:** pedir cotización por WhatsApp a [Farallones](https://farallonesrentacar.com/listavehiculos/) o [WayCarCali](https://waycarcali.com/) para la **entrega en el aeropuerto coordinando el vuelo de las 8 pm** y el total exacto de los 3 días. Si en cambio usan el mostrador (Kayak), reservar recogida fuera de horario (24 h de aviso) por si el vuelo se retrasa.
- **El reloj corre:** cuatro semanas y fin de semana de Halloween. Lo bueno se reserva primero.

---
*Documentos hermanos: Mini-Boom-en-Cali_Informe-completo.md · Mini-Boom-en-Cali_Resumen-ejecutivo.pdf · Mini-Boom-en-Cali_Resultados.xlsx · Mini-Boom-en-Cali_Presentacion.pptx. Generados desde una única fuente de datos (`src/generar_entregables.py`); cambiar un número regenera los cuatro en coherencia.*