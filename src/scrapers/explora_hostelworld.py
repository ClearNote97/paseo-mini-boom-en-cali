"""
explora_hostelworld.py — Tanteo (sandbox) del scraper de estadía con Playwright.

OBJETIVO
--------
Aprender Playwright barriendo hostales de Cali en Hostelworld para nuestras fechas
(30 oct - 2 nov 2026, 7 personas). Es un script de EXPLORACIÓN: acá ensayamos selectores
y vemos qué trae la página. Cuando la lógica funcione, el parser "limpio" se gradúa a
`src/` (reutilizable) y su verificación a `tests/` (el gate). Ver el flujo en README_AGENTS.md.

POR QUÉ HOSTELWORLD Y NO BOOKING/AIRBNB (de entrada)
----------------------------------------------------
Hostelworld renderiza resultados con menos anti-bot que Booking/Airbnb, así que es el mejor
sitio para APRENDER sin pelear con captchas. Una vez domines el patrón acá, adaptarlo a
Booking/Airbnb es el mismo esquema: navegar -> esperar -> localizar -> extraer.

CÓMO CORRERLO (dentro de tu devcontainer)
-----------------------------------------
1) Instala Playwright y su navegador (uv gestiona las deps del proyecto):
       uv add playwright
       uv run playwright install chromium      # baja el binario del navegador
2) Ejecuta:
       uv run python sandbox/explora_hostelworld.py
3) Mira la consola (lista de hostales) y el screenshot que deja en sandbox/ para
   inspeccionar el DOM cuando un selector no encuentre nada.

APRENDER-HACIENDO
-----------------
- Corre primero con HEADLESS=False para VER el navegador moverse (entiendes qué pasa).
- Si un selector no trae nada, la página cambió su HTML: usa el screenshot + el inspector
  de Playwright (`uv run playwright codegen https://www.hostelworld.com`) para hallar el
  selector nuevo. Los selectores de sitios comerciales cambian seguido: es parte del juego.
"""

from __future__ import annotations

import asyncio
import re
from pathlib import Path

from playwright.async_api import async_playwright

# ─── Parámetros del viaje (cámbialos acá, no en el código de abajo) ──────────────
CIUDAD_URL = "https://www.hostelworld.com/hostels/south-america/colombia/cali/"
CHECK_IN = "2026-10-30"   # viernes
CHECK_OUT = "2026-11-02"  # lunes (3 noches)
HUESPEDES = 7
HEADLESS = True           # ponlo en False la primera vez para VER el navegador
SCREENSHOT = Path(__file__).parent / "hostelworld_cali.png"

# Hostelworld acepta fechas y huéspedes por query string. Si el formato cambia, este es
# justo el tipo de cosa que ajustarás inspeccionando la URL real en tu navegador.
URL_BUSQUEDA = f"{CIUDAD_URL}?from={CHECK_IN}&to={CHECK_OUT}&guests={HUESPEDES}"


async def main() -> None:
    async with async_playwright() as p:
        # 1) Lanzar el navegador. chromium es el más estable para scraping.
        navegador = await p.chromium.launch(headless=HEADLESS)

        # Un 'context' es como una sesión de navegador aislada. Le damos un user-agent
        # realista y viewport de escritorio: sitios comerciales tratan distinto a headless "pelado".
        contexto = await navegador.new_context(
            user_agent=(
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1366, "height": 900},
            locale="es-CO",
        )
        pagina = await contexto.new_page()

        print(f"→ Abriendo {URL_BUSQUEDA}")
        # LECCIÓN: 'networkidle' falla en sitios comerciales (analytics constante hace que
        # la red nunca "descanse" y el goto expira). Usamos 'domcontentloaded' (se cumple
        # apenas llega el HTML) y luego esperamos a mano a que el JS pinte los resultados.
        try:
            await pagina.goto(URL_BUSQUEDA, wait_until="domcontentloaded", timeout=45_000)
        except Exception as e:
            print(f"  ⚠ goto lento/parcial: {type(e).__name__} — sigo igual para diagnosticar")

        # 2) Aceptar el banner de cookies si aparece (si no, seguimos sin drama).
        for texto_boton in ("Aceptar", "Accept", "Aceptar todo", "Got it"):
            try:
                await pagina.get_by_role("button", name=texto_boton).click(timeout=2_500)
                print(f"  cookies: clic en '{texto_boton}'")
                break
            except Exception:
                continue

        # Dar tiempo a que el JS pinte los resultados (los sitios cargan las tarjetas
        # DESPUÉS del HTML inicial). Intentamos esperar un contenedor típico de resultados.
        try:
            await pagina.wait_for_selector("[class*='property'], article", timeout=15_000)
        except Exception:
            print("  ⚠ no apareció contenedor de resultados en 15s (revisa el screenshot)")
        await pagina.wait_for_timeout(4_000)

        # Diagnóstico: título de la página (si dice 'Access denied'/captcha, lo sabremos).
        print(f"  título: {await pagina.title()!r}")

        # 3) Screenshot SIEMPRE (aunque falle la extracción): es tu mejor herramienta
        #    de depuración para ver qué renderizó realmente la página.
        await pagina.screenshot(path=str(SCREENSHOT), full_page=True)
        print(f"  screenshot guardado en {SCREENSHOT}")

        # 4) Localizar las tarjetas de hostales. OJO: este selector es una HIPÓTESIS.
        #    Si trae 0 resultados, ábrelo con codegen y ajústalo — ese es el ejercicio.
        tarjetas = pagina.locator("[class*='property-card'], article, [data-testid*='property']")
        n = await tarjetas.count()
        print(f"\n→ Encontré {n} tarjetas candidatas (si es 0, el selector cambió: revisa el screenshot)\n")

        # 5) Extraer campos de cada tarjeta, defensivamente (el sitio no siempre trae todo).
        for i in range(min(n, 25)):  # cap de 25 para no saturar mientras exploras
            tarjeta = tarjetas.nth(i)
            nombre = await _texto(tarjeta, "h2, h3, [class*='name'], [class*='title']")
            precio = await _texto(tarjeta, "[class*='price'], [class*='Price']")
            rating = await _texto(tarjeta, "[class*='rating'], [class*='score']")
            # Limpiar a valores atómicos: primer monto CO$ y primer número de rating.
            priv = _primer_monto(precio)
            punt = _primer_numero(rating)
            if nombre:
                print(f"  • {nombre:<40} | privada desde: {priv or 's/priv':>10} | rating: {punt or '?'}")

        await navegador.close()
        print("\n✔ Listo. Siguiente paso: cuando la extracción sea confiable, mueve la lógica")
        print("  de parseo a src/ y escribe un test en tests/ que valide el esquema de datos.")


def _primer_monto(texto: str | None) -> str | None:
    """Extrae el primer monto tipo 'CO$30000.00' de un bloque de texto."""
    if not texto:
        return None
    m = re.search(r"CO\$[\d.,]+", texto)
    return m.group(0) if m else None


def _primer_numero(texto: str | None) -> str | None:
    """Extrae el primer número (rating) de un bloque de texto."""
    if not texto:
        return None
    m = re.search(r"\b(10|\d\.\d|\d)\b", texto)
    return m.group(0) if m else None


async def _texto(scope, selector: str) -> str | None:
    """Devuelve el texto del primer elemento que matchee, o None. Nunca lanza excepción."""
    try:
        loc = scope.locator(selector).first
        if await loc.count() == 0:
            return None
        return (await loc.inner_text()).strip()
    except Exception:
        return None


if __name__ == "__main__":
    asyncio.run(main())
