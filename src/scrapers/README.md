# `src/scrapers/` — recolectores de datos

Scripts de recolección usados para armar el dossier **Mini-Boom en Cali**. Están en `src/`
(versionados) porque son la base reutilizable; sus salidas de depuración (capturas `.png`,
volcados `.txt`) **no** se versionan (ver `.gitignore` local).

> **Entorno:** se ejecutan dentro del Dev Container (que tiene red y navegador). Desde la raíz
> del proyecto: `uv run python src/scrapers/<archivo>.py`. Playwright requiere, una sola vez,
> `uv add playwright && uv run playwright install chromium`.

| Script | Qué hace |
|---|---|
| `explora_hostelworld.py` | Barre hostales de Cali en Hostelworld con las fechas reales y 7 huéspedes; extrae nombre, precio de habitación privada y rating. Base de los datos de estadía. |
| `explora_fichas.py` | Abre la ficha de cada candidato top para intentar sacar tipos de habitación y capacidad. |
| `explora_kayak.py` | Lee ofertas de alquiler de 7 puestos en Kayak (aeropuerto de Cali) para las fechas. |
| `download_flag.py` | Descarga la bandera de Cali (Wikimedia Commons) a `output/assets/`. |
| `download_cartagena.py` | Descarga la bandera de Cartagena a `output/assets/`. |

**Lecciones de Playwright integradas** (útiles para adaptarlos a otros sitios): `networkidle`
no sirve en sitios comerciales (usar `domcontentloaded` + espera explícita); `inner_text` trae
bloques que se limpian con regex; y la captura de pantalla es la mejor herramienta de
depuración cuando un selector deja de encontrar.

> Nota: los selectores de sitios comerciales cambian seguido. Si un script deja de extraer,
> revisá la captura y reajustá el selector (`uv run playwright codegen <url>`).
