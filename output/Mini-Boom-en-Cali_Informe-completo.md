# Mini-Boom en Cali
### Dossier de logística · transporte y estadía para siete

![Cartagena](./assets/flag_cartagena.png) → ![Cali](./assets/flag_cali.png)  
*De Cartagena a Cali.*

*Informe completo · 30 de septiembre de 2026. Lo acompañan un [resumen ejecutivo](./Mini-Boom-en-Cali_Resumen-ejecutivo.pdf), una [hoja de cálculo](./Mini-Boom-en-Cali_Resultados.xlsx) y una [presentación](./Mini-Boom-en-Cali_Presentacion.pptx).*

---

## Índice

1. [Punto de partida](#punto-de-partida)
2. [Cómo se hizo esto](#cómo-se-hizo-esto)
3. [Geografía de la seguridad](#geografía-de-la-seguridad)
4. [Estadía: el puntaje y los finalistas](#estadía-el-puntaje-y-los-finalistas)
5. [Movilidad: ¿en el aeropuerto o en la ciudad?](#movilidad-en-el-aeropuerto-o-en-la-ciudad)
6. [Movilidad: cuánto carro llevar](#movilidad-cuánto-carro-llevar)
7. [Cuatro lecturas del presupuesto](#cuatro-lecturas-del-presupuesto)
8. [La recomendación](#la-recomendación)
9. [Lo que queda por confirmar](#lo-que-queda-por-confirmar)

---

## Punto de partida

Siete personas, tres noches, una ciudad que premia al que planea. Del viernes 30 de octubre al lunes 2 de noviembre de 2026 —fin de semana de Halloween, con Cali en su punto más salsero y más lleno—. Se sale de Cartagena a las 7:00 am del 30 y se regresa en el vuelo de las 9:00 pm del 2: la pregunta no es cómo llegar, sino cómo movernos por la ciudad y dónde dormir sin que el presupuesto ni la seguridad cedan.

El margen es explícito: **$300.000 a $400.000 por persona** entre transporte y estadía, con licencia de estirar hasta **$480.000** cuando la calidad lo amerite. Y una condición innegociable: la seguridad va primero. Después, lo que hace memorable un viaje —piscina para el calor, aire para la noche, cocina para no dejar el sueldo en restaurantes, y la rumba a pie.

## Cómo se hizo esto

Esto se armó como un pequeño proyecto de datos, no a ojo. El orden importa:

1. **Primero la vara, después la búsqueda.** Se fijaron los pesos de cada criterio —con la seguridad mandando— antes de mirar un solo precio, para no dejarse llevar por la primera opción bonita.
2. **Precios reales, no de folleto.** Un navegador automatizado (Playwright) recorrió Hostelworld con las fechas exactas y siete huéspedes; el transporte se cotizó contra la búsqueda real de Kayak y contra agencias locales de Cali.
3. **Un puntaje propio y auditable** para la estadía (se explica más abajo), separado de la calificación de huéspedes de las plataformas.
4. **Una sola fuente de datos** genera estos cuatro documentos: si un número cambia, los cuatro se actualizan en coherencia.

## Geografía de la seguridad

Cali se lee por barrios. Donde el viajero duerme tranquilo y amanece cerca de todo: **San Antonio, Granada, El Peñón, Santa Teresita, Ciudad Jardín**. San Antonio —casas de colores, cuestas empedradas, salsa en cada esquina— es el favorito por razón. Lo que conviene esquivar: **Aguablanca (oriente), Siloé, Terrón Colorado (ladera oeste alta)**; la última es la subida al oeste alto, y suele ofrecerse disfrazada de ganga con vista.

## Estadía: el puntaje y los finalistas

El **9.6 o 9.8** junto a cada hostal es la calificación de huéspedes de Hostelworld, un dato externo. La decisión no se apoyó en ese número: se construyó un puntaje propio, de 0 a 100, con una nota de 1 a 5 por criterio multiplicada por su peso.

| Criterio | Peso | Cómo se asigna la nota (1–5) |
|---|:--:|---|
| Seguridad del barrio | 30% | Por zona (San Antonio / Granada / El Peñón = 5) |
| Amenidades y comodidad | 20% | Aire acondicionado +2, piscina +2, cocina +1 (tope 5) |
| Precio por persona | 20% | El más barato = 5; escala lineal hasta el más caro = 1 |
| Cercanía a zona turística | 12% | Qué tan a pie queda de lo turístico |
| Parqueadero | 10% | Disponibilidad estimada *(baja certeza)* |
| Ambiente social | 8% | Facilidad para conocer gente |

> **Fórmula:** puntaje = suma de (peso × nota⁄5). Con el líder, Viajero Hostel & Salsa School: 30×5⁄5 + 20×4⁄5 + 20×1.9⁄5 + 12×5⁄5 + 10×2⁄5 + 8×5⁄5 = **77.6/100**.

Ordenados por ese puntaje propio. La última columna es para juzgar con ojos propios:

| # | Hostal | Zona | Puntaje | Calificación huéspedes | Aire | Piscina | Estadía por persona (3 noches) | Ver |
|:--:|---|---|:--:|:--:|:--:|:--:|--:|:--:|
| 1 | Viajero Hostel & Salsa School ★ | San Antonio | **77.6** | 9.6 | ✔ | ✔ | $252.282 | [link](https://www.hostelworld.com/hostels/p/73676/viajero-cali-hostel-and-salsa-school/) |
| 2 | La Palmera Hostel | San Antonio | **75.8** | 9.7 | — | ✔ | $150.000 | [link](https://www.hostelworld.com/hostels/p/314482/la-palmera-hostel/) |
| 3 | Oasis Cali Hostel | Granada | **75.4** | 9.6 | ✔ | — | $150.000 | [link](https://www.hostelworld.com/hostels/p/284050/oasis-cali-hostel/) |
| 4 | La Chanca Hostel | San Antonio | **74.8** | 9.8 | — | — | $89.850 | [link](https://www.hostelworld.com/hostels/p/329092/la-chanca-hostel/) |
| 5 | Hostal Patio del Río | Oeste (Cali) | **72.8** | 9.6 | ✔ | ✔ | $189.750 | [link](https://www.hostelworld.com/hostels/p/323610/hostal-patio-del-rio/) |
| 6 | Casa/Apto entero (Airbnb) | San Antonio (Oeste) | **71.2** | — | ✔ | ✔ | $300.000 | [link](https://www.airbnb.com/s/San-Antonio--Cali--Valle-del-Cauca/homes?checkin=2026-10-30&checkout=2026-11-02&adults=7) |

- **[Viajero Hostel & Salsa School](https://www.hostelworld.com/hostels/p/73676/viajero-cali-hostel-and-salsa-school/)** — AC, piscina, bar, clases de salsa gratis, desayuno. El más completo en amenidades y ambiente.
- **[La Palmera Hostel](https://www.hostelworld.com/hostels/p/314482/la-palmera-hostel/)** — Privadas con ventilador (no AC) y balcón con vista. Clases de salsa. Rating 9.7.
- **[Oasis Cali Hostel](https://www.hostelworld.com/hostels/p/284050/oasis-cali-hostel/)** — En Granada, zona gastronómica y segura. Clases de salsa, tours, desayuno.
- **[La Chanca Hostel](https://www.hostelworld.com/hostels/p/329092/la-chanca-hostel/)** — El mejor rating del barrido (9.8) y el más económico. Amenidades básicas con cocina.
- **[Hostal Patio del Río](https://www.hostelworld.com/hostels/p/323610/hostal-patio-del-rio/)** — Piscina y AC. Equilibrio entre amenidades y precio, dentro de la meta.
- **[Casa/Apto entero (Airbnb)](https://www.airbnb.com/s/San-Antonio--Cali--Valle-del-Cauca/homes?checkin=2026-10-30&checkout=2026-11-02&adults=7)** — Casa entera de 4 habitaciones con piscina, AC y cocina. Máxima privacidad; estimado ~300k por persona (3 noches).

## Movilidad: ¿en el aeropuerto o en la ciudad?

**En el aeropuerto, sin dudarlo. No hay que elegir entre barato y cómodo: hay agencias locales —más económicas que las marcas grandes— que o tienen oficina en el propio aeropuerto (Farallones) o llevan el carro hasta allá sin costo cuando el alquiler es de 3 días o más (WayCarCali). Se aterriza, se recoge el carro ahí mismo y se devuelve en el aeropuerto antes de volar. Ir hasta la ciudad a buscarlo solo agregaría un taxi y tiempo, sin ahorrar nada.**

Un detalle de horarios: el alquiler se cobra por días de 24 horas desde que se recoge, con una hora de gracia. Como se llega la mañana del 30 y se vuela a las 9 de la noche del 2, conservar el carro hasta esa noche cruza a un cuarto día de alquiler. Vale la pena: ese último tramo —entre dejar el hostal al mediodía y el vuelo de la noche— es justo cuando más sirve el carro, con las maletas ya encima. Si se devuelve de noche, conviene avisar a la agencia con un día de anticipación.

## Movilidad: cuánto carro llevar

Resuelto el *dónde*, queda el *cuánto*: tres formas de moverse, de la más cómoda a la más barata. Todas con costo todo-incluido por persona (grupo de 7, con gasolina y taxis donde aplican).

| Opción | Qué implica | Por persona | Comodidad | Ver |
|---|---|--:|---|:--:|
| **Carro propio todo el viaje, recogido en el aeropuerto** ★ | Una van de 7 puestos de agencia local, recogida y devuelta en el mismo aeropuerto, manejándola ustedes, con la gasolina ya contada. | **$150.000** | La más cómoda: carro desde que aterrizan hasta que abordan, y libertad para salir de Cali cuando quieran (Pance, Calima). | [ver](https://farallonesrentacar.com/listavehiculos/) |
| **Carro propio, pero solo tres días** | Se devuelve al mediodía del último día para no pagar el cuarto día; esa última tarde se mueven en taxi, ya con las maletas. | **$140.000** | Ahorro pequeño; la última tarde quedan sin carro y cargando maletas. | [ver](https://www.kayak.com.co/cars/Santiago-de-Cali,Colombia-c11092/2026-10-30/2026-11-02;map?fs=carcapacity=precise_7;carlocationid=~CLO&ucs=9x1xcq&sort=rank_a) |
| **Sin carro propio: taxis y una van con conductor para el paseo de afuera** | Taxis y apps dentro de la ciudad, más una van con conductor contratada solo para el día que salgan de Cali. | **$125.000** | La más barata y sin manejar ni parquear; a cambio, menos libertad para salir de improviso. | [ver](https://carrent.com.co/alquiler-de-van-en-cali) |

> El mostrador de las marcas grandes en el aeropuerto costaría casi el doble (~$235.000 por persona): con las agencias locales que entregan allá mismo, no hace falta.

**Cómo cambia el total** con el hostal recomendado (Viajero, $252.282 por persona de estadía):

| Estadía + forma de moverse | Total por persona | En el bolsillo |
|---|--:|:--:|
| Viajero + sin carro propio | **$377.282** | DENTRO |
| Viajero + carro propio | **$392.282** | DENTRO |
| Viajero + carro propio todo el viaje ★ | **$402.282** | FLEX |

## Cuatro lecturas del presupuesto

Cada lectura combina un hostal con la movilidad recomendada (Carro propio todo el viaje, recogido en el aeropuerto, $150.000 por persona). Con otra forma de moverse, el total se corre según la tabla de arriba.

| Lectura | Estadía | Total por persona | En el bolsillo |
|---|---|--:|:--:|
| **Económico** | [La Chanca Hostel](https://www.hostelworld.com/hostels/p/329092/la-chanca-hostel/) | **$239.850** | DENTRO |
| **Amenidades en meta** | [Hostal Patio del Río](https://www.hostelworld.com/hostels/p/323610/hostal-patio-del-rio/) | **$339.750** | DENTRO |
| **El equilibrio** ★ | [Viajero Hostel & Salsa School](https://www.hostelworld.com/hostels/p/73676/viajero-cali-hostel-and-salsa-school/) | **$402.282** | FLEX |
| **Casa entera** | [Casa/Apto entero (Airbnb)](https://www.airbnb.com/s/San-Antonio--Cali--Valle-del-Cauca/homes?checkin=2026-10-30&checkout=2026-11-02&adults=7) | **$450.000** | FLEX |

## La recomendación

**Viajero Hostel & Salsa School (estadía) + carro propio todo el viaje recogido en el aeropuerto ≈ $402.282 por persona.** El hostal responde que sí a cada exigencia a la vez —zona más segura y caminable, piscina, aire, bar y rumba a un costado, y las clases de salsa que resuelven eso de conocer gente—. Y la movilidad recomendada da carro todos los días sin vueltas a la ciudad ni hueco final con maletas, más barato que el mostrador de las marcas grandes.

Palancas según la prioridad: si manda el ahorro, moverse **sin carro propio** baja el total a $377.282 (entra en meta), a cambio de menos libertad para salir de Cali; si lo que pesa es no pasar de 400 mil en estadía, **[Hostal Patio del Río](https://www.hostelworld.com/hostels/p/323610/hostal-patio-del-rio/)** ($339.750) mantiene piscina y aire.

## Lo que queda por confirmar

Las cartas boca arriba:

- **Estadía:** ¿el precio es por persona o por habitación? Se asumió por persona (lo prudente). Y confirmar capacidad para siete con camas mínimo cinco al abrir cada ficha.
- **Movilidad:** una llamada por WhatsApp a [Farallones](https://farallonesrentacar.com/listavehiculos/) o [WayCarCali](https://waycarcali.com/) para cerrar la van de 7 puestos en las fechas, confirmar la entrega en el aeropuerto y el precio del cuarto día.
- **El reloj corre:** cinco semanas y fin de semana de Halloween. Lo bueno se reserva primero.

---
*Documentos hermanos: Mini-Boom-en-Cali_Informe-completo.md · Mini-Boom-en-Cali_Resumen-ejecutivo.pdf · Mini-Boom-en-Cali_Resultados.xlsx · Mini-Boom-en-Cali_Presentacion.pptx. Generados desde una única fuente de datos (`src/generar_entregables.py`); cambiar un número regenera los cuatro en coherencia.*