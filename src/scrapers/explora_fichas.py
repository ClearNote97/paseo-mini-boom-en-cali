"""
explora_fichas.py — Segunda iteración: abrir la FICHA de cada candidato top.

El listado da "Privates From CO$X" pero NO dice si es por persona o por habitación,
ni la capacidad. Eso vive en la ficha de cada hostal. Este script:
  1) Barre el listado y captura el enlace (href) de los candidatos de interés.
  2) Abre cada ficha con las fechas y vuelca las filas de habitaciones (tipo + precio).

Correr:  uv run python sandbox/explora_fichas.py
"""

from __future__ import annotations

import asyncio

from playwright.async_api import async_playwright

CIUDAD_URL = "https://www.hostelworld.com/hostels/south-america/colombia/cali/"
CHECK_IN, CHECK_OUT, HUESPEDES = "2026-10-30", "2026-11-02", 7
URL_BUSQUEDA = f"{CIUDAD_URL}?from={CHECK_IN}&to={CHECK_OUT}&guests={HUESPEDES}"

# Candidatos que nos interesan (substring del nombre, en minúsculas).
CANDIDATOS = ["viajero", "patio del", "palmera", "oasis", "chanca"]


async def main() -> None:
    async with async_playwright() as p:
        navegador = await p.chromium.launch(headless=True)
        ctx = await navegador.new_context(
            user_agent=(
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1366, "height": 900},
            locale="es-CO",
        )
        pagina = await ctx.new_page()

        # 1) Listado -> capturar enlaces de los candidatos
        try:
            await pagina.goto(URL_BUSQUEDA, wait_until="domcontentloaded", timeout=45_000)
        except Exception as e:
            print(f"goto listado: {type(e).__name__}")
        await pagina.wait_for_timeout(6_000)

        enlaces: dict[str, str] = {}
        anclas = pagina.locator("a[href*='/hostels/p/']")
        for i in range(await anclas.count()):
            a = anclas.nth(i)
            href = await a.get_attribute("href")
            txt = ((await a.inner_text()) or "").strip().lower()
            if not href:
                continue
            for cand in CANDIDATOS:
                if cand in txt and cand not in enlaces:
                    url = href if href.startswith("http") else f"https://www.hostelworld.com{href}"
                    enlaces[cand] = url.split("?")[0]
        print(f"→ Enlaces encontrados: {list(enlaces.keys())}\n")

        # 2) Abrir cada ficha con fechas y volcar filas con precio
        for cand, url in enlaces.items():
            ficha = f"{url}?from={CHECK_IN}&to={CHECK_OUT}&guests={HUESPEDES}"
            print(f"\n===== {cand.upper()} =====\n{ficha}")
            try:
                await pagina.goto(ficha, wait_until="domcontentloaded", timeout=45_000)
                await pagina.wait_for_timeout(6_000)
            except Exception as e:
                print(f"  goto ficha: {type(e).__name__}")
                continue
            # Volcar líneas del cuerpo que mencionen precio o tipo de habitación.
            cuerpo = await pagina.inner_text("body")
            claves = ("CO$", "Private", "Privada", "Dorm", "bed", "cama", "Room", "Ensuite")
            vistas: set[str] = set()
            for linea in cuerpo.splitlines():
                l = linea.strip()
                if l and any(k in l for k in claves) and len(l) < 80 and l not in vistas:
                    vistas.add(l)
                    print(f"  | {l}")

        await navegador.close()


if __name__ == "__main__":
    asyncio.run(main())
