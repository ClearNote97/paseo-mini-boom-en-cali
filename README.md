# 🌴 Mini-Boom en Cali

> Planear un viaje grupal, resuelto como un **mini-proyecto de datos**.
> Lo valioso de este repo **no es el destino: es el método** — cómo se abordó un problema real,
> ambiguo y con plata de por medio, de forma rigurosa, honesta y reproducible, en colaboración
> con un agente de IA.

Siete personas, un fin de semana en Cali, presupuesto ajustado y la seguridad como regla de oro.
En vez de resolverlo "a ojo" en un grupo de WhatsApp, se abordó como se aborda un problema de datos:
**definir la vara → recolectar datos reales → puntuar con transparencia → consolidar → decidir**, dejando
el razonamiento trazado en una bitácora de decisiones.

El resultado son cuatro documentos (informe, resumen ejecutivo, hoja de cálculo y presentación) — pero
lo que se busca *evidenciar* es el **proceso de pensamiento** detrás de ellos.

---

## 🧩 El problema

- **Grupo:** 7 personas (mixto, comparten cuartos).
- **Fechas:** 30 oct – 2 nov 2026 (viernes a lunes, 3 noches). Ida 6:00 pm desde Cartagena, **llega 8:00 pm**; regreso en vuelo 9:00 pm del 2.
- **Presupuesto:** $300–400k COP por persona (transporte + estadía), con flex hasta $480k si la calidad lo amerita.
- **Prioridad innegociable:** la seguridad. Después: piscina, aire, cocina, rumba cerca y ambiente social.
- **Dos decisiones a resolver:** dónde dormir y cómo movilizarse dentro de la ciudad.

---

## 🧠 Cómo se abordó (lo valioso)

El corazón del proyecto es el *método*, no la respuesta:

1. **Criterio antes que búsqueda.** Primero se fijaron los pesos de cada criterio (seguridad 30%, amenidades,
   precio, cercanía, parqueadero, ambiente) — *antes* de mirar un solo precio, para no sesgar la decisión
   por la primera opción atractiva.
2. **Precios reales, no de folleto.** Un navegador automatizado (Playwright) recorrió Hostelworld y Airbnb
   (casas/aptos enteros) con las fechas exactas y 7 huéspedes; el transporte se cotizó contra Kayak y
   agencias locales de Cali.
3. **Puntaje propio y auditable.** Se construyó un puntaje 0–100 (nota 1–5 por criterio × su peso), **distinto**
   del rating externo de las plataformas, con la fórmula a la vista.
4. **Consolidación por trade-off**, no solo por precio: arquetipos de estadía y escenarios de movilidad.
5. **Honestidad sobre supuestos y límites.** Se marca qué es dato real, qué es estimado y qué falta confirmar
   (p. ej. precio por persona vs. por habitación; tarifas locales de alquiler corto).
6. **Una sola fuente de datos** (`src/generar_entregables.py`) genera los 4 documentos en coherencia: cambiar
   un número los actualiza a todos.
7. **Bitácora de decisiones** (`docs/bitacora-decisiones.md`, `D-001`…`D-004`) como **evidencia del razonamiento**:
   qué se decidió, por qué, qué se descartó y qué cambió cuando cambiaron las condiciones (p. ej. el vuelo
   pasó a llegar de noche → se reajustó solo la movilidad).

> **Iteración humano–IA.** Buena parte del valor está en el ida y vuelta: el humano define el problema, pone
> la vara, corrige supuestos (cuando el agente calculó mal el precio de la Captiva, el humano lo cachó y se
> corrigió) y decide; el agente ejecuta la recolección, el cálculo, la maquetación y deja todo trazado.

---

## 📦 Entregables

Generados en [`output/`](./output/) — los cuatro se referencian entre sí y comparten estándar visual
(paleta cálida pastel, tarjetas redondeadas, banderas Cartagena → Cali):

| Archivo | Qué es |
|---|---|
| `Mini-Boom-en-Cali_Informe-completo.md` | Informe completo: metodología, criterios, datos, análisis, recomendación y límites. |
| `Mini-Boom-en-Cali_Resumen-ejecutivo.pdf` | Resumen ejecutivo de una mirada. |
| `Mini-Boom-en-Cali_Resultados.xlsx` | Resultados numéricos, una hoja por tema (estadía, movilidad, vehículos, puntaje). |
| `Mini-Boom-en-Cali_Presentacion.pptx` | Presentación visual para contarlo al grupo. |

---

## 🛠️ Stack y herramientas

**Entorno y lenguaje**
- **Python 3.14** gestionado con **`uv`** (lockfile reproducible).
- **Dev Container + Docker** (VS Code) — toolchain aislado, sin instalar nada en el host.
- **Plantilla base:** [**ClearNote Py DA**](https://github.com/ClearNote97/ClearNote_Py_DA) — plantilla propia de
  dev container para análisis de datos en Python (ver créditos).

**Recolección de datos (web scraping)**
- **Playwright** (Chromium) — scraping de sitios que cargan con JavaScript (Hostelworld, Kayak).
- `urllib` — descarga de activos (banderas desde Wikimedia Commons).

**Generación de documentos**
- **openpyxl** → Excel · **python-pptx** → PowerPoint · **reportlab** → PDF · **Pillow** → imágenes.
- **PyMuPDF** + **LibreOffice** (headless) — para *renderizar y verificar visualmente* cada documento antes de entregarlo.
- **pandas / numpy / pyarrow** — disponibles para el manejo de datos.

**Fuentes de datos consultadas**
- Hostelworld (estadía), Kayak (alquiler de vehículos), Airbnb (casa entera), sitios de agencias locales
  (Farallones, WayCarCali), tarifas oficiales de taxi de Cali, Wikimedia Commons (banderas).

**Agente de IA (par de trabajo) — incluyéndolo explícitamente**
- Todo el análisis, el scraping y la maquetación se construyeron en colaboración con un **agente de IA**:
  **Claude** (Anthropic), operado a través de **Claude Code**, dentro del marco personal de agentes **Helix**.
- El rol humano fue **dirigir**: definir el problema, fijar criterios, corregir supuestos y decidir.
  El rol del agente fue **ejecutar**: recolectar, calcular, maquetar y dejar el razonamiento trazado en la bitácora.

---

## ▶️ Cómo reproducirlo

> Todo corre **dentro del Dev Container** (ahí viven Python, `uv` y el navegador).

```bash
# 1. Abrir el repo en VS Code → "Reopen in Container" (el postCreate corre `uv sync`)

# 2. (una sola vez) instalar el navegador de Playwright
uv run playwright install --with-deps chromium

# 3. Recolectar datos (opcional — re-scrapea precios frescos)
uv run python src/scrapers/explora_hostelworld.py
uv run python src/scrapers/explora_kayak.py

# 4. Generar los 4 documentos desde la fuente única de datos
uv run python src/generar_entregables.py
#    → deja todo en output/
```

Los scrapers viven en [`src/scrapers/`](./src/scrapers/) (con su propio README). Los selectores de sitios
comerciales cambian seguido: si uno deja de extraer, se ajusta con la captura de pantalla + `playwright codegen`.

---

## 🗂️ Estructura

```
.
├── src/
│   ├── generar_entregables.py   # fuente única de datos → genera los 4 documentos
│   └── scrapers/                # recolectores (Playwright) + descarga de banderas
├── docs/
│   ├── bitacora-decisiones.md   # el PORQUÉ de cada decisión (D-001…D-004) — la evidencia del método
│   └── diccionario-de-datos.md  # qué significa cada variable
├── output/                      # los 4 entregables + assets (banderas)
├── .devcontainer/               # definición del entorno (Dev Container + uv)
└── README.md                    # este archivo (el caso de estudio)
```

---

## ⚠️ Nota honesta

Esto es una **ayuda a la decisión**, no una reserva. Los precios son de referencia (algunos reales/scrapeados,
otros estimados y marcados como tales) y deben confirmarse antes de reservar. El valor del repo está en *cómo
se pensó el problema*, no en que cada cifra sea definitiva.

---

## 🙏 Créditos

- **Plantilla base:** [ClearNote Py DA](https://github.com/ClearNote97/ClearNote_Py_DA) — dev container para análisis de datos en Python.
- **Autor:** MSc. Nicolás Enrique Valencia Santiago.
- **Par de trabajo:** agente de IA (Claude / Claude Code, en el marco Helix).
- Plantilla enriquecida con la asistencia de [Helix](https://github.com/ftuga/helix_asisten) de [ftuga](https://github.com/ftuga).

## ⚖️ Licencia

[MIT](https://opensource.org/license/MIT).
