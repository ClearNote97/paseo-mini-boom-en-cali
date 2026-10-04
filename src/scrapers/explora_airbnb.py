"""
explora_airbnb.py — Scraper de estadía (casas/aptos enteros) en Airbnb con Playwright.

OBJETIVO
--------
Barrer Airbnb buscando **alojamientos enteros** (casa o apartamento completo, no habitación
suelta) para nuestras fechas y grupo (30 oct - 2 nov 2026, 7 personas) en zonas seguras de
Cali (San Antonio / Granada / Oeste). Es el complemento de `explora_hostelworld.py`: aquí
el atractivo es la **privacidad total** — baños del grupo, sin compartir con extraños.

POR QUÉ AIRBNB (y por qué es más difícil que Hostelworld)
---------------------------------------------------------
Airbnb renderiza todo con JS y tiene anti-bot agresivo (puede devolver captcha o página
vacía a un navegador headless "pelado"). Por eso este script es DEFENSIVO: user-agent real,
viewport de escritorio, esperas a mano, screenshot + volcado de HTML SIEMPRE, y varios
selectores de respaldo. Si Airbnb bloquea, el screenshot/HTML lo deja en evidencia y se
cae a investigación manual (marcada como estimada en los entregables).

CÓMO CORRERLO (dentro del devcontainer)
---------------------------------------
    uv run playwright install chromium        # si no está el binario
    uv run python src/scrapers/explora_airbnb.py

Deja en src/scrapers/: airbnb_cali.png (screenshot) y airbnb_body.txt (texto visible),
para inspeccionar el DOM si un selector no encuentra nada. Imprime en consola una lista de
candidatos (nombre · precio · link).
"""

from __future__ import annotations

import asyncio
import json
import re
from pathlib import Path
from urllib.parse import quote

from playwright.async_api import async_playwright

# ─── Parámetros del viaje (cámbialos acá, no en el código de abajo) ──────────────
CHECK_IN = "2026-10-30"   # viernes
CHECK_OUT = "2026-11-02"  # lunes (3 noches)
ADULTOS = 7
# Noroeste / oeste de Cali, cerca de la zona de actividades (Av. Sexta, Granada, El Peñón, Oeste).
ZONAS = [
    "Granada, Cali, Valle del Cauca",
    "Santa Mónica, Cali, Valle del Cauca",
    "Versalles, Cali, Valle del Cauca",
    "El Peñón, Cali, Valle del Cauca",
    "Santa Teresita, Cali, Valle del Cauca",
    "Centenario, Cali, Valle del Cauca",
    "Normandía, Cali, Valle del Cauca",
    "La Flora, Cali, Valle del Cauca",
    "Prados del Norte, Cali, Valle del Cauca",
    "San Antonio, Cali, Valle del Cauca",
]
HEADLESS = True           # ponlo en False la primera vez para VER el navegador
AQUI = Path(__file__).parent
SCREENSHOT = AQUI / "airbnb_cali.png"
BODY_DUMP = AQUI / "airbnb_body.txt"
JSON_OUT = AQUI / "airbnb_resultados.json"


def url_busqueda(zona: str) -> str:
    """Arma la URL de resultados de Airbnb filtrando por alojamiento entero."""
    destino = quote(zona)
    return (
        f"https://www.airbnb.com/s/{destino}/homes"
        f"?checkin={CHECK_IN}&checkout={CHECK_OUT}"
        f"&adults={ADULTOS}&room_types[]=Entire%20home%2Fapt"
        f"&currency=COP&locale=es"
    )


async def _texto(scope, selector: str) -> str | None:
    """Texto del primer elemento que matchee, o None. Nunca lanza."""
    try:
        loc = scope.locator(selector).first
        if await loc.count() == 0:
            return None
        return (await loc.inner_text()).strip()
    except Exception:
        return None


async def _attr(scope, selector: str, attr: str) -> str | None:
    try:
        loc = scope.locator(selector).first
        if await loc.count() == 0:
            return None
        return await loc.get_attribute(attr)
    except Exception:
        return None


def _primer_monto_cop(texto: str | None) -> int | None:
    """Extrae el primer monto en COP (p.ej. '$ 1.234.567' o 'COP 1,234,567') como entero."""
    if not texto:
        return None
    # Normaliza: nos quedamos con el primer bloque largo de dígitos (con . o , de miles).
    m = re.search(r"(\$|COP)\s*([\d.,]{4,})", texto)
    if not m:
        return None
    digitos = re.sub(r"[.,]", "", m.group(2))
    return int(digitos) if digitos.isdigit() else None


async def barrer_zona(contexto, zona: str) -> list[dict]:
    pagina = await contexto.new_page()
    url = url_busqueda(zona)
    print(f"\n→ [{zona}] {url}")
    try:
        await pagina.goto(url, wait_until="domcontentloaded", timeout=45_000)
    except Exception as e:
        print(f"  ⚠ goto lento/parcial: {type(e).__name__} — sigo para diagnosticar")

    # Banner de cookies / idioma, si aparece.
    for texto_boton in ("Aceptar", "Accept", "Aceptar todo", "OK", "De acuerdo"):
        try:
            await pagina.get_by_role("button", name=texto_boton).click(timeout=2_500)
            print(f"  cookies: clic en '{texto_boton}'")
            break
        except Exception:
            continue

    # Esperar a que pinten las tarjetas (Airbnb usa data-testid='card-container').
    try:
        await pagina.wait_for_selector(
            "[data-testid='card-container'], [itemprop='itemListElement']", timeout=20_000
        )
    except Exception:
        print("  ⚠ no apareció contenedor de tarjetas en 20s (revisa screenshot/body)")
    await pagina.wait_for_timeout(4_000)

    # Scroll para que Airbnb cargue (lazy) todas las tarjetas de la página, no solo las primeras.
    for _ in range(6):
        await pagina.mouse.wheel(0, 4_000)
        await pagina.wait_for_timeout(1_200)
    await pagina.wait_for_timeout(1_500)

    titulo = await pagina.title()
    print(f"  título: {titulo!r}")

    # Diagnóstico SIEMPRE: screenshot + texto visible (para la primera zona basta).
    try:
        await pagina.screenshot(path=str(SCREENSHOT), full_page=True)
        cuerpo = await pagina.locator("body").inner_text()
        BODY_DUMP.write_text(cuerpo[:20_000], encoding="utf-8")
        print(f"  screenshot → {SCREENSHOT.name} · body → {BODY_DUMP.name}")
    except Exception as e:
        print(f"  ⚠ no pude volcar diagnóstico: {type(e).__name__}")

    if re.search(r"captcha|verif|robot|unusual traffic|acceso denegado", (titulo or "").lower()):
        print("  🛑 parece pantalla anti-bot — caer a investigación manual")
        await pagina.close()
        return []

    tarjetas = pagina.locator("[data-testid='card-container'], [itemprop='itemListElement']")
    n = await tarjetas.count()
    print(f"  → {n} tarjetas candidatas")

    resultados: list[dict] = []
    for i in range(min(n, 30)):
        t = tarjetas.nth(i)
        nombre = (
            await _texto(t, "[data-testid='listing-card-title']")
            or await _texto(t, "[id^='title_']")
            or await _texto(t, "meta[itemprop='name']")
        )
        # El precio total del periodo suele venir en el texto de la tarjeta ("$X total").
        bloque = await _texto(t, "[data-testid='price-availability-row']") or await _texto(t, "*")
        total = None
        if bloque:
            m_total = re.search(r"([\d.,]{4,})\s*(COP\s*)?total", bloque, re.I)
            total = _primer_monto_cop(m_total.group(0)) if m_total else _primer_monto_cop(bloque)
        # Rating: Airbnb lo pone como "4,95 (123)" en el texto de la tarjeta.
        rating, resenas = None, None
        card_txt = await _texto(t, "*")
        if card_txt:
            m_r = re.search(r"\b([45],\d{1,2})\s*\((\d+)\)", card_txt)
            if m_r:
                rating = float(m_r.group(1).replace(",", "."))
                resenas = int(m_r.group(2))
        href = await _attr(t, "a[href*='/rooms/']", "href")
        link = f"https://www.airbnb.com{href.split('?')[0]}" if href else None
        subt = await _texto(t, "[data-testid='listing-card-subtitle']")
        if nombre:
            resultados.append(
                {"zona": zona.split(",")[0], "nombre": nombre, "total_periodo": total,
                 "subtitulo": subt, "rating": rating, "resenas": resenas, "link": link}
            )
            print(f"    • {nombre[:38]:<38} | {total or '?':>9} | ★{rating or '?'} ({resenas or '?'}) | {subt or ''}")

    await pagina.close()
    return resultados


async def main() -> None:
    async with async_playwright() as p:
        navegador = await p.chromium.launch(headless=HEADLESS)
        contexto = await navegador.new_context(
            user_agent=(
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1366, "height": 900},
            locale="es-CO",
        )
        todo: list[dict] = []
        for zona in ZONAS:
            try:
                todo.extend(await barrer_zona(contexto, zona))
            except Exception as e:
                print(f"  ⚠ zona '{zona}' falló: {type(e).__name__}: {e}")
        await navegador.close()

        JSON_OUT.write_text(json.dumps(todo, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\n✔ {len(todo)} candidatos totales guardados en {JSON_OUT.name}")
        if not todo:
            print("  (vacío → Airbnb bloqueó o cambió el DOM: revisa airbnb_cali.png / airbnb_body.txt)")


if __name__ == "__main__":
    asyncio.run(main())
