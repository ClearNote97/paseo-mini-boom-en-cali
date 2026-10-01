"""Descarga la bandera de Cartagena (PNG) vía API de Wikimedia Commons. Se ejecuta en el devcontainer."""
from __future__ import annotations
import json, urllib.parse, urllib.request
from pathlib import Path

DEST = Path(__file__).resolve().parents[2] / "output" / "assets" / "flag_cartagena.png"
DEST.parent.mkdir(parents=True, exist_ok=True)
TITULOS = [
    "File:Flag of Cartagena.svg",
    "File:Flag of Cartagena (Colombia).svg",
    "File:Bandera de Cartagena.svg",
    "File:Flag of Cartagena, Bolívar.svg",
    "File:Bandera de Cartagena de Indias.svg",
]
API = "https://commons.wikimedia.org/w/api.php"
UA = "Cali2026-TravelPlanner/1.0 (educational trip planning)"

def resolver(titulo, width=640):
    q = urllib.parse.urlencode({"action": "query", "titles": titulo, "prop": "imageinfo",
                                "iiprop": "url", "iiurlwidth": width, "format": "json"})
    req = urllib.request.Request(f"{API}?{q}", headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=25) as r:
        data = json.load(r)
    for _, page in data.get("query", {}).get("pages", {}).items():
        info = page.get("imageinfo")
        if info:
            return info[0].get("thumburl") or info[0].get("url")
    return None

for t in TITULOS:
    try:
        url = resolver(t)
    except Exception as e:
        print(f"  {t}: error {type(e).__name__}"); continue
    if not url:
        print(f"  {t}: sin imageinfo"); continue
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=25) as r:
            DEST.write_bytes(r.read())
        print(f"✔ Cartagena de '{t}' -> {DEST} ({DEST.stat().st_size} bytes)")
        break
    except Exception as e:
        print(f"  {t}: error descarga {type(e).__name__}")
else:
    print("✗ No se pudo descargar la bandera de Cartagena.")
