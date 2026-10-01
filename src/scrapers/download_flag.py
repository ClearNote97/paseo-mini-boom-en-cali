"""Descarga la bandera de Santiago de Cali (PNG) vía la API de Wikimedia Commons.
Se ejecuta DENTRO del devcontainer (que tiene red). Guarda en output/assets/flag_cali.png."""
from __future__ import annotations

import json
import urllib.parse
import urllib.request
from pathlib import Path

DEST = Path(__file__).resolve().parents[2] / "output" / "assets" / "flag_cali.png"
DEST.parent.mkdir(parents=True, exist_ok=True)

# Títulos candidatos del archivo en Commons (probamos en orden).
TITULOS = [
    "File:Flag of Cali.svg",
    "File:Bandera de Cali.svg",
    "File:Flag of Santiago de Cali.svg",
    "Flag of Cali.svg",
]
API = "https://commons.wikimedia.org/w/api.php"
UA = "Cali2026-TravelPlanner/1.0 (educational trip planning)"


def resolver_thumb(titulo: str, width: int = 640) -> str | None:
    q = urllib.parse.urlencode(
        {
            "action": "query",
            "titles": titulo,
            "prop": "imageinfo",
            "iiprop": "url",
            "iiurlwidth": width,
            "format": "json",
        }
    )
    req = urllib.request.Request(f"{API}?{q}", headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=25) as r:
        data = json.load(r)
    pages = data.get("query", {}).get("pages", {})
    for _, page in pages.items():
        info = page.get("imageinfo")
        if info:
            return info[0].get("thumburl") or info[0].get("url")
    return None


def main() -> None:
    for titulo in TITULOS:
        try:
            url = resolver_thumb(titulo)
        except Exception as e:
            print(f"  {titulo}: error API {type(e).__name__}")
            continue
        if not url:
            print(f"  {titulo}: sin imageinfo")
            continue
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=25) as r:
                DEST.write_bytes(r.read())
            print(f"✔ Bandera descargada de '{titulo}' -> {DEST} ({DEST.stat().st_size} bytes)")
            return
        except Exception as e:
            print(f"  {titulo}: error descarga {type(e).__name__}")
    print("✗ No se pudo descargar la bandera; la presentación usará un placeholder.")


if __name__ == "__main__":
    main()
