"""explora_kayak.py — Lee ofertas de alquiler 7-puestos en Kayak (CLO) para las fechas reales.
Kayak carga con JS y tiene anti-bot; por eso hace falta navegador real. Correr en el devcontainer:
    uv run python sandbox/explora_kayak.py
"""
from __future__ import annotations

import asyncio
import re
from pathlib import Path

from playwright.async_api import async_playwright

URL = ("https://www.kayak.com.co/cars/Santiago-de-Cali,Colombia-c11092/2026-10-30/2026-11-02;map"
       "?fs=carcapacity=precise_7;carlocationid=~CLO&ucs=9x1xcq&sort=rank_a")
SHOT = Path(__file__).parent / "kayak_cali.png"


async def main() -> None:
    async with async_playwright() as p:
        nav = await p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
        ctx = await nav.new_context(
            user_agent=("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"),
            viewport={"width": 1440, "height": 1000}, locale="es-CO")
        pg = await ctx.new_page()
        try:
            await pg.goto(URL, wait_until="domcontentloaded", timeout=60_000)
        except Exception as e:
            print(f"goto: {type(e).__name__}")
        # Kayak tarda en poblar; damos margen y hacemos scroll para disparar carga.
        await pg.wait_for_timeout(12_000)
        for _ in range(4):
            await pg.mouse.wheel(0, 3000)
            await pg.wait_for_timeout(2500)
        print("título:", repr(await pg.title()))
        await pg.screenshot(path=str(SHOT), full_page=True)
        print("screenshot:", SHOT)

        cuerpo = await pg.inner_text("body")
        (Path(__file__).parent / "kayak_body.txt").write_text(cuerpo, encoding="utf-8")
        # ¿Bloqueo/captcha?
        low = cuerpo.lower()
        if any(k in low for k in ("captcha", "verify you are human", "acceso denegado", "unusual traffic")):
            print("⚠ Posible bloqueo anti-bot (captcha). Revisar screenshot.")
        # Volcar líneas con precios COP y agencias/vehículos
        agencias = ("localiza", "hertz", "avis", "national", "alamo", "enterprise", "sixt", "budget",
                    "green motion", "dollar", "thrifty", "europcar", "keddy", "sunnycars", "flexways")
        vistas: set[str] = set()
        for linea in cuerpo.splitlines():
            l = linea.strip()
            if not l or l in vistas:
                continue
            if re.search(r"(COL?\$|\bCOP\b|\$\s?\d)", l) or any(a in l.lower() for a in agencias) \
               or re.search(r"\b\d+\s*(pasajer|asient|puesto)", l.lower()):
                if len(l) < 90:
                    vistas.add(l)
                    print(f"  | {l}")

        await nav.close()


if __name__ == "__main__":
    asyncio.run(main())
