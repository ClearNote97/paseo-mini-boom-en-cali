"""
explora_fichas_airbnb.py — Detalle (ficha) de alojamientos de Airbnb con Playwright.

Toma una lista de URLs /rooms/ (las mejores candidatas que salieron de explora_airbnb.py) y
abre cada ficha para extraer lo que la tarjeta de resultados NO trae: capacidad real, número
de habitaciones, camas y sobre todo **baños** (la dimensión que al grupo le importa: no
compartir baño con extraños) y amenidades clave (aire, piscina, cocina).

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

# Candidatas a verificar (id → etiqueta corta). Las que mejor cuadran con 7 personas / baño propio.
FICHAS = {
    "38526055": "Casa 7 personas con garaje",
    "1048602132521468133": "Casa 4 Habitaciones - Terraza y Aire",
    "1505090686623655075": "Casa Familiar 5 Hab con Terraza",
    "880582897050465656": "Casa para 8 personas",
    "825481159079037573": "Casa con piscina privada",
    "47950307": "Apto El Ingenio 301",
}


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
    """Baños pueden ser '2.5' (medio baño). Devuelve float o None."""
    m = re.search(r"(\d+(?:[.,]5)?)\s*ba[ñn]os?", texto, re.I)
    if not m:
        return None
    return float(m.group(1).replace(",", "."))


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
    await pagina.wait_for_timeout(4_000)
    txt = await _body(pagina)

    # Línea de resumen típica: "7 huéspedes · 3 habitaciones · 5 camas · 2 baños"
    datos = {
        "id": room_id, "etiqueta": etiqueta, "url": url.split("?")[0],
        "huespedes": _num(r"(\d+)\s*hu[eé]spedes", txt),
        "habitaciones": _num(r"(\d+)\s*(?:habitaci[oó]n|dormitorio|rec[aá]mara)", txt),
        "camas": _num(r"(\d+)\s*camas?", txt),
        "banos": _banos(txt),
        "aire": bool(re.search(r"aire acondicionado", txt, re.I)),
        "piscina": bool(re.search(r"piscina", txt, re.I)),
        "cocina": bool(re.search(r"\bcocina\b", txt, re.I)),
        "titulo": (await pagina.title()).split(" - Airbnb")[0] if txt else None,
    }
    print(f"  {datos['huespedes']}h · {datos['habitaciones']}hab · {datos['camas']}camas · "
          f"{datos['banos']}baños | aire:{datos['aire']} piscina:{datos['piscina']} cocina:{datos['cocina']}")
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
