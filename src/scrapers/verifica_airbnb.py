"""
verifica_airbnb.py — Verificación DURA de disponibilidad y amenidades de alojamientos Airbnb.

Dos cosas que el scraping "de texto" no resolvía bien y que el usuario tuvo que cazar a mano:

1) DISPONIBILIDAD para las fechas exactas. Se intercepta la llamada real de Airbnb
   (PdpAvailabilityCalendar) que trae, por día: available / availableForCheckin /
   availableForCheckout / minNights. Con eso se decide si el rango 30 oct → 2 nov 2026
   (noches del 30, 31 y 1; salida el 2) es reservable de verdad.

2) AMENIDADES. Se abre la página de amenidades (/rooms/<id>/amenities), que lista TODO lo que
   el lugar ofrece (y lo que NO), sin el ruido del carrusel de "similares". Se corta en la
   sección "no ofrece" para no contar como disponible algo que está tachado.

Corre en el devcontainer:
    uv run python src/scrapers/verifica_airbnb.py
Deja src/scrapers/airbnb_verificacion.json con el veredicto por ficha.
"""

from __future__ import annotations

import asyncio
import json
import re
from pathlib import Path

from playwright.async_api import async_playwright

CHECK_IN = "2026-10-30"
CHECK_OUT = "2026-11-02"
NOCHES = ["2026-10-30", "2026-10-31", "2026-11-01"]  # las 3 que necesitamos
SALIDA = "2026-11-02"
ADULTOS = 7
AQUI = Path(__file__).parent
JSON_OUT = AQUI / "airbnb_verificacion.json"

IDS = {
    "1556929420516931269": "[NUEVO user] opción 1",
    "1727019164229496188": "[NUEVO user] opción 2",
    "1277005393867902776": "[NUEVO user] opción 3",
    "49124373": "[NUEVO user] Apto tranquilo",
}


def _walk_dias(obj, acc):
    """Recorre el JSON y junta todos los dicts con 'calendarDate'."""
    if isinstance(obj, dict):
        if "calendarDate" in obj:
            acc[obj["calendarDate"]] = obj
        for v in obj.values():
            _walk_dias(v, acc)
    elif isinstance(obj, list):
        for v in obj:
            _walk_dias(v, acc)


def _veredicto_disp(dias: dict) -> tuple[str, dict]:
    """Decide si el rango es reservable con los días del calendario."""
    detalle = {}
    for f in NOCHES + [SALIDA]:
        d = dias.get(f)
        if d is None:
            detalle[f] = "?"
        else:
            detalle[f] = {"avail": d.get("available"), "in": d.get("availableForCheckin"),
                          "out": d.get("availableForCheckout"), "min": d.get("minNights")}
    if any(detalle[f] == "?" for f in NOCHES):
        return "DESCONOCIDO", detalle
    noches_ok = all(isinstance(detalle[f], dict) and detalle[f]["avail"] for f in NOCHES)
    checkin_ok = isinstance(detalle[NOCHES[0]], dict) and detalle[NOCHES[0]]["in"] is not False
    salida_ok = (detalle[SALIDA] == "?" or (isinstance(detalle[SALIDA], dict)
                 and detalle[SALIDA]["out"] is not False))
    minn = detalle[NOCHES[0]].get("min") if isinstance(detalle[NOCHES[0]], dict) else None
    min_ok = (minn is None) or (minn <= 3)
    ok = noches_ok and checkin_ok and salida_ok and min_ok
    return ("DISPONIBLE" if ok else "NO"), detalle


async def disponibilidad(contexto, rid: str) -> tuple[str, dict]:
    pagina = await contexto.new_page()
    url = (f"https://www.airbnb.com/rooms/{rid}?check_in={CHECK_IN}&check_out={CHECK_OUT}"
           f"&adults={ADULTOS}&currency=COP&locale=es")
    dias: dict = {}
    try:
        async with pagina.expect_response(
            lambda r: "PdpAvailabilityCalendar" in r.url, timeout=30_000
        ) as ri:
            await pagina.goto(url, wait_until="domcontentloaded", timeout=45_000)
            # Forzar la apertura del calendario por si la llamada no sale sola.
            for sel in ('[data-testid="change-dates-checkIn"]', 'text=/Check-?in/i',
                        'text=/Llegada/i', '[data-is-day-blocked]'):
                try:
                    await pagina.click(sel, timeout=2_500)
                    break
                except Exception:
                    continue
            await pagina.wait_for_timeout(6_000)
        resp = await ri.value
        data = await resp.json()
        _walk_dias(data, dias)
    except Exception as e:
        print(f"    ⚠ calendario no capturado: {type(e).__name__}")
    await pagina.close()
    return _veredicto_disp(dias)


async def amenidades(contexto, rid: str) -> dict:
    pagina = await contexto.new_page()
    url = (f"https://www.airbnb.com/rooms/{rid}/amenities?adults={ADULTOS}&locale=es&currency=COP")
    txt = ""
    try:
        await pagina.goto(url, wait_until="domcontentloaded", timeout=45_000)
        await pagina.wait_for_timeout(4_000)
        try:
            txt = await pagina.locator('[role="dialog"]').inner_text(timeout=4_000)
        except Exception:
            txt = await pagina.locator("body").inner_text()
    except Exception as e:
        print(f"    ⚠ amenidades no leídas: {type(e).__name__}")
    await pagina.close()
    # Cortar en la sección "no ofrece" para no contar amenidades tachadas.
    corte = re.search(r"(no ofrece|no incluye|not included|lo que este lugar no)", txt, re.I)
    disp = txt[:corte.start()] if corte else txt
    return {
        "ac": bool(re.search(r"aire acondicionado", disp, re.I)),
        "piscina": bool(re.search(r"\bpiscina\b", disp, re.I)),
        "cocina": bool(re.search(r"\bcocina\b", disp, re.I)),
        "parqueadero": bool(re.search(r"estacionamiento|parqueadero|garaje|parking", disp, re.I)),
        "leido": bool(txt),
    }


async def main() -> None:
    async with async_playwright() as p:
        navegador = await p.chromium.launch(headless=True)
        contexto = await navegador.new_context(
            user_agent=("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"),
            viewport={"width": 1366, "height": 900}, locale="es-CO",
        )
        out = []
        for rid, et in IDS.items():
            print(f"\n→ {et} ({rid})")
            disp, detalle = await disponibilidad(contexto, rid)
            amen = await amenidades(contexto, rid)
            print(f"    disponibilidad 30→2: {disp}  | aire:{amen['ac']} piscina:{amen['piscina']} "
                  f"cocina:{amen['cocina']} parq:{amen['parqueadero']}")
            out.append({"id": rid, "etiqueta": et, "disponible": disp, "detalle_dias": detalle,
                        "amenidades": amen})
        await navegador.close()
        JSON_OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\n✔ {len(out)} verificaciones en {JSON_OUT.name}")


if __name__ == "__main__":
    asyncio.run(main())
