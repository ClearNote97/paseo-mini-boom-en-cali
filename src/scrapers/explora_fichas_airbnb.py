"""
explora_fichas_airbnb.py — Detalle (ficha) de alojamientos de Airbnb con Playwright.

Toma una lista de URLs /rooms/ (las mejores candidatas que salieron de explora_airbnb.py) y
abre cada ficha para extraer: capacidad, habitaciones, camas y **baños**, más amenidades
clave (aire, piscina, cocina), el rating y una pista del barrio. Datos para puntuar las casas
con la MISMA fórmula que los hostales (ver D-005).

Nota anti-ruido: el texto de la ficha incluye un carrusel de "alojamientos similares" que
contamina la detección de amenidades (aparece 'piscina' de OTRO anuncio). Por eso recortamos
el cuerpo en el primer marcador de esa sección antes de buscar amenidades.

Corre dentro del devcontainer:
    uv run python src/scrapers/explora_fichas_airbnb.py
Deja src/scrapers/airbnb_fichas.json con el detalle por ficha.
"""

from __future__ import annotations

import asyncio
import json
import re
from pathlib import Path

from playwright.async_api import async_playwright

CHECK_IN = "2026-10-30"
CHECK_OUT = "2026-11-02"
ADULTOS = 7
AQUI = Path(__file__).parent
JSON_OUT = AQUI / "airbnb_fichas.json"

# Candidatas del occidente / zona de actividades a verificar (id → etiqueta corta).
FICHAS = {
    "1048602132521468133": "Casa 4 Habitaciones - Terraza y Aire",
    "38526055": "Casa 7 personas con garaje",
    "1071190715409487725": "Casa Amplia y Cómoda en Las Flores",
    "1538036648539244464": "Apto familiar ubicación estratégica",
    "934280562272881551": "Apto grande y tranquilo",
    "880582897050465656": "Casa para 8 personas (Granada)",
    "49321247": "Casa Bella, bohemia San Antonio",
    "1699978286025248131": "Apto moderno con piscina",
    "1590016903260349041": "L2 - San Antonio (balcón)",
    "825481159079037573": "Casa con piscina privada",
}

# Marcadores donde empieza el carrusel de 'similares' (cortamos el body ahí). OJO: NO cortar en
# "Anfitrión:" — eso aparece ANTES de la sección de amenidades y nos la perderíamos.
_CORTE = re.compile(r"(Lugares para alojarse similares|Alojamientos similares|Explora otras opciones|"
                    r"Otros alojamientos que te pueden gustar|Puede que también te guste)", re.I)


def url_ficha(room_id: str) -> str:
    return (f"https://www.airbnb.com/rooms/{room_id}"
            f"?check_in={CHECK_IN}&check_out={CHECK_OUT}&adults={ADULTOS}&currency=COP&locale=es")


async def _body(pagina) -> str:
    try:
        return await pagina.locator("body").inner_text()
    except Exception:
        return ""


def _num(patron: str, texto: str) -> int | None:
    m = re.search(patron, texto, re.I)
    return int(m.group(1)) if m else None


def _banos(texto: str) -> float | None:
    m = re.search(r"(\d+(?:[.,]5)?)\s*ba[ñn]os?", texto, re.I)
    return float(m.group(1).replace(",", ".")) if m else None


async def ficha(contexto, room_id: str, etiqueta: str) -> dict:
    pagina = await contexto.new_page()
    url = url_ficha(room_id)
    print(f"\n→ {etiqueta} ({room_id})")
    try:
        await pagina.goto(url, wait_until="domcontentloaded", timeout=45_000)
    except Exception as e:
        print(f"  ⚠ goto: {type(e).__name__}")
    for b in ("Aceptar", "Accept", "OK", "De acuerdo"):
        try:
            await pagina.get_by_role("button", name=b).click(timeout=2_000)
            break
        except Exception:
            continue
    await pagina.wait_for_timeout(4_500)
    txt_full = await _body(pagina)
    # Recortar el carrusel de similares para no contaminar amenidades.
    corte = _CORTE.search(txt_full)
    txt = txt_full[:corte.start()] if corte else txt_full

    # Rating: "4,92" o "4.92" cerca de "reseñas"/"evaluaciones", o patrón "4,9 · 123 reseñas".
    rating = None
    m_rat = re.search(r"\b([45][.,]\d{1,2})\b(?=[^\n]{0,40}(rese|evalua|calif|★))", txt_full, re.I)
    if not m_rat:
        m_rat = re.search(r"\b([45][.,]\d{1,2})\b", txt_full)
    if m_rat:
        rating = float(m_rat.group(1).replace(",", "."))

    # Barrio: de la sección "Dónde vas a estar/Dónde estarás" (primera línea tras el heading).
    barrio = None
    m_b = re.search(r"D[oó]nde (?:vas a estar|estar[aá]s)\s*\n+\s*([A-ZÁÉÍÓÚ][^\n,]{2,40})", txt_full)
    if m_b:
        barrio = m_b.group(1).strip()

    datos = {
        "id": room_id, "etiqueta": etiqueta, "url": url.split("?")[0],
        "huespedes": _num(r"(\d+)\s*hu[eé]spedes", txt),
        "habitaciones": _num(r"(\d+)\s*(?:habitaci[oó]n|dormitorio|rec[aá]mara)", txt),
        "camas": _num(r"(\d+)\s*camas?", txt),
        "banos": _banos(txt),
        "aire": bool(re.search(r"aire acondicionado", txt, re.I)),
        "piscina": bool(re.search(r"piscina", txt, re.I)),
        "cocina": bool(re.search(r"\bcocina\b", txt, re.I)),
        "parqueadero": bool(re.search(r"estacionamiento|parqueadero|garaje|parking", txt, re.I)),
        "rating": rating,
        "barrio": barrio,
        "titulo": (await pagina.title()).split(" - Airbnb")[0],
    }
    print(f"  {datos['huespedes']}h · {datos['habitaciones']}hab · {datos['camas']}camas · "
          f"{datos['banos']}baños | aire:{datos['aire']} pisc:{datos['piscina']} parq:{datos['parqueadero']} "
          f"| ★{datos['rating']} | barrio:{datos['barrio']}")
    await pagina.close()
    return datos


async def main() -> None:
    async with async_playwright() as p:
        navegador = await p.chromium.launch(headless=True)
        contexto = await navegador.new_context(
            user_agent=("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"),
            viewport={"width": 1366, "height": 900}, locale="es-CO",
        )
        out = []
        for rid, et in FICHAS.items():
            try:
                out.append(await ficha(contexto, rid, et))
            except Exception as e:
                print(f"  ⚠ {rid} falló: {type(e).__name__}: {e}")
        await navegador.close()
        JSON_OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\n✔ {len(out)} fichas guardadas en {JSON_OUT.name}")


if __name__ == "__main__":
    asyncio.run(main())
