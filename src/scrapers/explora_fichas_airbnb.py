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

# Candidatas a verificar (id → etiqueta corta). Se edita por iteración.
FICHAS = {
    "28196917": "Apartamento cerca Estadio",
    "1538036648539244464": "Apto familiar ubicación estratégica",
    "1754825634045341668": "Apartamento con Aire (Santa Mónica)",
    "1524138619210052243": "Apartamento familiar / Excelente ubicación",
    "1465402516514594759": "Vive la experiencia – Moderno apto",
    "961489175423000977": "Chalet el Encanto",
    "49124373": "Apto tranquilo para compartir",
    "1112396000580569933": "Espacioso refugio 3 dorm – Vistas",
    "1271933838955311814": "Luxury apartamento Cali 501",
    "880582897050465656": "Casa para 8 personas",
}

# Anclas de la "zona de actividades" del noroeste/oeste (Granada y El Peñón / Av. Sexta).
ANCLA_LAT, ANCLA_LNG = 3.4535, -76.5345  # punto medio Granada–El Peñón
CALI_LAT_RANGE = (3.30, 3.52)
CALI_LNG_RANGE = (-76.60, -76.44)

# Marcadores donde empieza el carrusel de 'similares' (cortamos el body ahí). OJO: NO cortar en
# "Anfitrión:" — eso aparece ANTES de la sección de amenidades y nos la perderíamos.
_CORTE = re.compile(r"(Lugares para alojarse similares|Alojamientos similares|Explora otras opciones|"
                    r"Otros alojamientos que te pueden gustar|Puede que también te guste)", re.I)


def url_ficha(room_id: str) -> str:
    return (f"https://www.airbnb.com/rooms/{room_id}"
            f"?check_in={CHECK_IN}&check_out={CHECK_OUT}&adults={ADULTOS}&currency=COP&locale=es")


def _coords(html: str) -> tuple[float, float] | None:
    """Extrae (lat, lng) del alojamiento del HTML. Toma el par más frecuente dentro de Cali
    (el punto del listado se repite en mapa/meta; los de 'similares' quedan en minoría)."""
    pares = re.findall(r'"l(?:at|atitude)":\s*(-?\d+\.\d+),\s*"l(?:ng|ongitude)":\s*(-?\d+\.\d+)', html)
    cont: dict[tuple[float, float], int] = {}
    for la, ln in pares:
        la, ln = float(la), float(ln)
        if CALI_LAT_RANGE[0] <= la <= CALI_LAT_RANGE[1] and CALI_LNG_RANGE[0] <= ln <= CALI_LNG_RANGE[1]:
            k = (round(la, 4), round(ln, 4))
            cont[k] = cont.get(k, 0) + 1
    return max(cont, key=cont.get) if cont else None


def _km_a_actividades(lat: float, lng: float) -> float:
    dy = (lat - ANCLA_LAT) * 111.0
    dx = (lng - ANCLA_LNG) * 110.8  # cos(3.45°) ≈ 0.998
    return round((dx * dx + dy * dy) ** 0.5, 1)


def _sector(lat: float, lng: float) -> str:
    """Clasificación aproximada por cuadrante de Cali."""
    if lng > -76.505:
        return "ESTE"
    if lat < 3.39:
        return "SUR"
    if lat >= 3.462 and lng <= -76.520:
        return "NOROESTE"
    if 3.425 <= lat < 3.462 and lng <= -76.532:
        return "OESTE"
    return "CENTRO/otro"


def _disponible(txt: str) -> bool | None:
    """Heurística de disponibilidad para las fechas pedidas (según la ficha con check_in/out)."""
    if re.search(r"no (?:est[aá]\s)?disponibl|not available|fechas no disponibles", txt, re.I):
        return False
    tiene_total = bool(re.search(r"(\$|COP)\s*[\d.,]{4,}", txt)) and bool(re.search(r"\btotal\b|noches", txt, re.I))
    return True if tiene_total else None


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
    try:
        html = await pagina.content()
    except Exception:
        html = ""
    # Recortar el carrusel de similares para no contaminar amenidades.
    corte = _CORTE.search(txt_full)
    txt = txt_full[:corte.start()] if corte else txt_full

    # Ubicación real por coordenadas (no por el título).
    coord = _coords(html)
    if coord:
        lat, lng = coord
        sector = _sector(lat, lng)
        km = _km_a_actividades(lat, lng)
    else:
        lat = lng = km = None
        sector = "?"
    disponible = _disponible(txt_full)

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
        "lat": lat, "lng": lng, "sector": sector, "km_actividades": km,
        "disponible_30": disponible,
        "titulo": (await pagina.title()).split(" - Airbnb")[0],
    }
    disp_txt = {True: "SÍ", False: "NO", None: "?"}[disponible]
    print(f"  {datos['huespedes']}h · {datos['habitaciones']}hab · {datos['camas']}camas · {datos['banos']}baños "
          f"| aire:{datos['aire']} pisc:{datos['piscina']} parq:{datos['parqueadero']} | ★{datos['rating']} "
          f"| {sector} ~{km}km act. | dispo30:{disp_txt}")
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
