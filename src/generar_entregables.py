"""
generar_entregables.py — Fuente única de datos + generador de los 4 entregables (v6 / planeación v2).

v2 (cambio de vuelo): la ida ahora sale 6 pm y llega 8 pm del 30 oct (antes, media mañana).
Impacto, solo en movilidad: (1) el viaje entra en 3 días de alquiler limpios (un día menos),
(2) la recogida es de noche — lo que mejor cuadra es una agencia local (Farallones/WayCarCali) que
entrega coordinando el vuelo; los mostradores de aeropuerto son más baratos pero cierran ~10 pm.

Produce en output/: *_Informe-completo.md, *_Resumen-ejecutivo.pdf, *_Resultados.xlsx,
*_Presentacion.pptx (se referencian entre sí). Correr:  uv run python src/generar_entregables.py
"""
from __future__ import annotations

import re
from pathlib import Path

# ─────────────── PALETA CÁLIDA PASTEL (roles) ───────────────
PRIMARY = "B5765C"
PRIMARY_DK = "8F5A44"
ACCENT = "D9A75E"
ACCENT_SOFT = "F0E0C6"
BG = "FCF5EC"
ALTROW = "F4E8DA"
INK = "463A32"
MUTE = "8A7A6E"
POSITIVE = "8B9B5E"
SOFTLINE = "E3D3C4"
WHITE = "FFFFFF"

# ─────────────── CONTEXTO ───────────────
CONTEXTO = {
    "titulo": "Mini-Boom en Cali",
    "subtitulo": "Dossier de logística · transporte y estadía para siete",
    "personas": 7,
    "fechas": "30 oct – 2 nov 2026 (viernes a lunes · 3 noches)",
    "horarios": "Ida 30 oct: sale 6:00 pm de Cartagena, llega 8:00 pm · regreso en vuelo 9:00 pm del 2 nov",
    "origen": "Cartagena — llegada en avión (Aeropuerto Alfonso Bonilla Aragón)",
    "meta_min": 300_000,
    "meta_max": 400_000,
    "techo": 480_000,
    "fecha_informe": "1 de octubre de 2026",
}

# ─────────────── LINKS ───────────────
KAYAK_URL = ("https://www.kayak.com.co/cars/Santiago-de-Cali,Colombia-c11092/2026-10-30/2026-11-02;map"
             "?fs=carcapacity=precise_7;carlocationid=~CLO&ucs=9x1xcq&sort=rank_a")
FARALLONES_URL = "https://farallonesrentacar.com/listavehiculos/"
WAYCAR_URL = "https://waycarcali.com/"
CARRENT_URL = "https://carrent.com.co/alquiler-de-van-en-cali"
TAXI_URL = "https://www.taxislibres.com.co/blog/tarifas-taxi-cali-decreto-1084-2025"

# ─────────────── ESTADÍA (scrapeado + evaluado) — sin cambios respecto a v1 ───────────────
ESTADIA = [
    {"nombre": "Viajero Hostel & Salsa School", "zona": "San Antonio", "rating_hw": 9.6,
     "priv_noche": 84094, "ac": True, "piscina": True, "cocina": False,
     "seguridad": 5, "social": 5, "parq": 2, "cercania": 5,
     "url": "https://www.hostelworld.com/hostels/p/73676/viajero-cali-hostel-and-salsa-school/",
     "nota": "AC, piscina, bar, clases de salsa gratis, desayuno. El más completo en amenidades y ambiente."},
    {"nombre": "La Palmera Hostel", "zona": "San Antonio", "rating_hw": 9.7,
     "priv_noche": 50000, "ac": False, "piscina": True, "cocina": False,
     "seguridad": 5, "social": 4, "parq": 2, "cercania": 5,
     "url": "https://www.hostelworld.com/hostels/p/314482/la-palmera-hostel/",
     "nota": "Privadas con ventilador (no AC) y balcón con vista. Clases de salsa. Rating 9.7."},
    {"nombre": "Oasis Cali Hostel", "zona": "Granada", "rating_hw": 9.6,
     "priv_noche": 50000, "ac": True, "piscina": False, "cocina": False,
     "seguridad": 5, "social": 4, "parq": 3, "cercania": 4,
     "url": "https://www.hostelworld.com/hostels/p/284050/oasis-cali-hostel/",
     "nota": "En Granada, zona gastronómica y segura. Clases de salsa, tours, desayuno."},
    {"nombre": "Hostal Patio del Río", "zona": "Oeste (Cali)", "rating_hw": 9.6,
     "priv_noche": 63250, "ac": True, "piscina": True, "cocina": False,
     "seguridad": 4, "social": 3, "parq": 3, "cercania": 4,
     "url": "https://www.hostelworld.com/hostels/p/323610/hostal-patio-del-rio/",
     "nota": "Piscina y AC. Equilibrio entre amenidades y precio, dentro de la meta."},
    {"nombre": "La Chanca Hostel", "zona": "San Antonio", "rating_hw": 9.8,
     "priv_noche": 29950, "ac": False, "piscina": False, "cocina": True,
     "seguridad": 5, "social": 3, "parq": 2, "cercania": 5,
     "url": "https://www.hostelworld.com/hostels/p/329092/la-chanca-hostel/",
     "nota": "El mejor rating del barrido (9.8) y el más económico. Amenidades básicas con cocina."},
    {"nombre": "Casa/Apto entero (Airbnb)", "zona": "San Antonio (Oeste)", "rating_hw": None,
     "priv_noche": 100000, "ac": True, "piscina": True, "cocina": True,
     "seguridad": 4, "social": 2, "parq": 4, "cercania": 5,
     "url": "https://www.airbnb.com/s/San-Antonio--Cali--Valle-del-Cauca/homes?checkin=2026-10-30&checkout=2026-11-02&adults=7",
     "nota": "Casa entera de 4 habitaciones con piscina, AC y cocina. Máxima privacidad; estimado ~300k por persona (3 noches)."},
]

PESOS_ESTADIA = [
    ("seguridad", "Seguridad del barrio", 30),
    ("amenidades", "Amenidades y comodidad (aire acondicionado, etc.)", 20),
    ("precio", "Precio por persona", 20),
    ("cercania", "Cercanía a zona turística", 12),
    ("parq", "Parqueadero", 10),
    ("social", "Ambiente social", 8),
]

# ─────────────── MOVILIDAD v2 (llegada de noche) ───────────────
LLEGADA = ("La llegada es a las 8 de la noche del 30, un viernes. El viaje entra en tres días de alquiler limpios "
           "(se recoge esa noche y se devuelve ~7 pm del 2, por debajo de las 72 horas). Para la hora, lo que "
           "mejor cuadra es una agencia local (Farallones, WayCarCali) que entrega el carro coordinando el vuelo. "
           "Los mostradores del aeropuerto (Alamo/Localiza) salen más baratos pero cierran ~10 pm, así que si se "
           "recoge ahí conviene reservar la recogida fuera de horario (24 h de aviso) por si el vuelo se retrasa. "
           "Y como red: los taxis oficiales del aeropuerto operan 24/7 (distintivo amarillo, tarifados, seguros).")

TIMING = ("El alquiler se cuenta por días de 24 horas desde la recogida, con una hora de gracia; con la llegada "
          "de noche, los tres días cuadran hasta la tarde del 2. El matiz, corregido: el mostrador del aeropuerto "
          "sale un poco más barato pero tiene horario rígido (cierra ~10 pm); una agencia local cuesta algo más y, "
          "a cambio, entrega coordinando el vuelo — que es lo que de verdad cuadra con una llegada a las 8 pm.")

MOVILIDAD = [
    {"nombre": "Carro propio entregado por una agencia local (cuadra con la llegada de noche)",
     "corto": "Carro local (entrega)", "pp": 200_000,
     "detalle": "Una agencia local (Farallones, WayCarCali) entrega el carro coordinando el vuelo, sin pelear con "
                "el horario del mostrador; ~3 días con gasolina. P. ej. la Captiva Turbo (~$1.200.000 / 3 días).",
     "flex": "La más libre y la que cuadra con la llegada de noche; cuesta un poco más que el mostrador.",
     "url": FARALLONES_URL, "recomendado": True},
    {"nombre": "Carro propio en el mostrador del aeropuerto (Kayak)", "corto": "Carro mostrador (Kayak)",
     "pp": 180_000,
     "detalle": "Más barato (p. ej. Nissan X-Trail $1.033.028 / 3 días), pero el mostrador (Alamo/Localiza) cierra "
                "~10 pm: con la llegada 8 pm va apretado, y si el vuelo se retrasa hay que reservar recogida fuera "
                "de horario (24 h de aviso).",
     "flex": "El carro más barato, pero el horario del mostrador aprieta con la llegada de noche.",
     "url": KAYAK_URL, "recomendado": False},
    {"nombre": "Sin carro propio: taxis y una van con conductor para el paseo de afuera", "corto": "Sin carro propio",
     "pp": 125_000,
     "detalle": "Taxi oficial de llegada (24/7), Uber/DiDi en la ciudad y una van con conductor contratada solo el "
                "día que salgan de Cali.",
     "flex": "La más barata y sin manejar ni parquear; menos ideal si quieren varias salidas de la ciudad.",
     "url": CARRENT_URL, "recomendado": False},
]
MOV_RECO = next(m for m in MOVILIDAD if m["recomendado"])
TRANSPORTE_REF = MOV_RECO["pp"]
MOV_MIN = min(m["pp"] for m in MOVILIDAD)
PALANCA = ("La diferencia clave no es tanto el precio como el horario: el mostrador del aeropuerto es un poco más "
           "barato pero cierra ~10 pm; una agencia local cuesta algo más y entrega coordinando el vuelo, que es "
           "lo que cuadra con la llegada de las 8 pm. Los totales de 3 días de las locales se cierran por WhatsApp.")

# Vehículos concretos de 7 puestos para las fechas (3 días, en el aeropuerto). Precio = total del periodo.
# Fuente: búsqueda real de Kayak (precise_7, CLO). 'maletas' = maletas grandes que admite.
VEHICULOS = [
    {"modelo": "Chevrolet Captiva Turbo", "agencia": "Farallones (local)", "tarifa": "~$1.200.000",
     "pp_txt": "$171.429", "fit": "Sí — oficina en el aeropuerto y domicilio",
     "url": "https://farallonesrentacar.com/car-model/captiva-turbo-7-puestos/"},
    {"modelo": "Toyota Fortuner", "agencia": "Farallones (local)", "tarifa": "desde $1.140.000",
     "pp_txt": "$162.857", "fit": "Sí — entrega coordinando el vuelo", "url": "https://farallonesrentacar.com/listavehiculos/"},
    {"modelo": "Mitsubishi Montero Sport", "agencia": "Farallones (local)", "tarifa": "desde $705.000",
     "pp_txt": "$100.714", "fit": "Sí — entrega coordinando el vuelo", "url": "https://farallonesrentacar.com/listavehiculos/"},
    {"modelo": "7 puestos (varios modelos)", "agencia": "WayCarCali (local)", "tarifa": "desde $360.000",
     "pp_txt": "$51.429", "fit": "Sí — domicilio gratis al aeropuerto (3+ días)", "url": WAYCAR_URL},
    {"modelo": "Nissan X-Trail", "agencia": "Kayak · EconomyBookings", "tarifa": "$1.033.028",
     "pp_txt": "$147.575", "fit": "Mostrador: cierra ~10 pm", "url": KAYAK_URL},
    {"modelo": "SUV mediano híbrido", "agencia": "Kayak · Alkilautos", "tarifa": "$1.847.639",
     "pp_txt": "$263.948", "fit": "Mostrador: cierra ~10 pm", "url": KAYAK_URL},
]
VEHICULOS_NOTA = ("Todos los precios son por los 3 días, solo el alquiler (sin gasolina ni parqueo). Las tarifas "
                  "locales 'desde' se calculan sobre la tarifa base/día × 3; en alquiler corto el total real suele "
                  "ser mayor (la Captiva, confirmada, cuesta ~$1.200.000) — pidan el exacto por WhatsApp. Lo clave "
                  "sigue siendo el horario: las locales entregan coordinando el vuelo; los mostradores cierran ~10 pm.")

ZONAS_SEGURAS = ["San Antonio", "Granada", "El Peñón", "Santa Teresita", "Ciudad Jardín"]
ZONAS_EVITAR = ["Aguablanca (oriente)", "Siloé", "Terrón Colorado (ladera oeste alta)"]

BASE = "Mini-Boom-en-Cali"
ARCHIVOS = {
    "md": f"{BASE}_Informe-completo.md",
    "pdf": f"{BASE}_Resumen-ejecutivo.pdf",
    "xlsx": f"{BASE}_Resultados.xlsx",
    "pptx": f"{BASE}_Presentacion.pptx",
}
ARCHIVOS_REF = " · ".join(ARCHIVOS.values())
OUT = Path(__file__).resolve().parent.parent / "output"
ASSETS = OUT / "assets"
FLAG_CALI = ASSETS / "flag_cali_rgb.png"
FLAG_CTG = ASSETS / "flag_cartagena_rgb.png"


def cop(v) -> str:
    if v is None:
        return "por cotizar"
    return "$" + format(int(round(v)), ",d").replace(",", ".")


def estado_pp(total: int) -> str:
    return "DENTRO" if total <= CONTEXTO["meta_max"] else ("FLEX" if total <= CONTEXTO["techo"] else "EXCEDE")


def _slug(t: str) -> str:
    t = t.lower()
    for ch in "¿?:()—,.¡!·":
        t = t.replace(ch, "")
    return re.sub(r"\s+", "-", t.strip())


# ─────────────── SCORING (estadía) — sin cambios ───────────────
def _pp_estadia(item: dict) -> int:
    if item["nombre"].startswith("Casa/Apto"):
        return 300_000
    return item["priv_noche"] * 3


def _sub_amenidades(e: dict) -> float:
    return max(1, min(5, (2 if e["ac"] else 0) + (2 if e["piscina"] else 0) + (1 if e["cocina"] else 0)))


def _sub_precio(e: dict) -> float:
    costos = [_pp_estadia(x) for x in ESTADIA]
    lo, hi = min(costos), max(costos)
    return 5.0 if hi == lo else round(1 + 4 * (hi - _pp_estadia(e)) / (hi - lo), 2)


def subnotas(e: dict) -> dict:
    return {"seguridad": float(e["seguridad"]), "amenidades": _sub_amenidades(e), "precio": _sub_precio(e),
            "cercania": float(e["cercania"]), "parq": float(e["parq"]), "social": float(e["social"])}


def puntaje(e: dict) -> float:
    sn = subnotas(e)
    return round(sum(peso * (sn[clave] / 5) for clave, _, peso in PESOS_ESTADIA), 1)


ESTADIA_RANK = sorted(ESTADIA, key=puntaje, reverse=True)
MEJOR = ESTADIA_RANK[0]


def _paquete(nombre, est_nombre, nota=""):
    est = next(e for e in ESTADIA if e["nombre"] == est_nombre)
    est_pp = _pp_estadia(est)
    total = est_pp + TRANSPORTE_REF
    return {"nombre": nombre, "estadia": est_nombre, "estadia_obj": est, "estadia_pp": est_pp,
            "transporte_pp": TRANSPORTE_REF, "total_pp": total, "estado": estado_pp(total),
            "recomendado": est is MEJOR, "nota": nota, "url": est["url"]}


PAQUETES = [
    _paquete("Económico", "La Chanca Hostel",
             "Máximo ahorro y el mejor rating del barrido (9.8). San Antonio, amenidades básicas."),
    _paquete("Amenidades en meta", "Hostal Patio del Río",
             "Piscina y aire acondicionado sin salir de los 400 mil. La alternativa prudente de presupuesto."),
    _paquete("El equilibrio", "Viajero Hostel & Salsa School",
             "Seguridad, piscina, aire, bar, rumba a pie y ambiente social. El puntaje más alto."),
    _paquete("Casa entera", "Casa/Apto entero (Airbnb)",
             "Máxima privacidad y comodidad (piscina, aire, cocina). Dentro del flex."),
]
RECO = next(p for p in PAQUETES if p["recomendado"])

SENSIBILIDAD = [
    {"mov": m, "total": _pp_estadia(MEJOR) + m["pp"], "estado": estado_pp(_pp_estadia(MEJOR) + m["pp"])}
    for m in sorted(MOVILIDAD, key=lambda x: x["pp"])
]

SEC = {
    "partida": "Punto de partida",
    "metodo": "Cómo se hizo esto",
    "seguridad": "Geografía de la seguridad",
    "estadia": "Estadía: el puntaje y los finalistas",
    "mov_donde": "Movilidad: la llegada es de noche",
    "mov_cuanto": "Movilidad: las tres opciones",
    "lecturas": "Cuatro lecturas del presupuesto",
    "reco": "La recomendación",
    "confirmar": "Lo que queda por confirmar",
}
# Etiqueta corta de la movilidad recomendada, para encabezados
MOV_RECO_LBL = "carro local (entrega coordinada)"


# ══════════════════════════════ 1) INFORME .MD ══════════════════════════════
def build_md() -> None:
    c = CONTEXTO
    L: list[str] = []
    A = L.append

    A(f"# {c['titulo']}")
    A(f"### {c['subtitulo']}\n")
    A("![Cartagena](./assets/flag_cartagena.png) → ![Cali](./assets/flag_cali.png)  ")
    A("*De Cartagena a Cali.*\n")
    A(f"*Informe completo · {c['fecha_informe']} · **planeación v2** (ajustada al nuevo horario de vuelo). "
      f"Lo acompañan un [resumen ejecutivo](./{ARCHIVOS['pdf']}), una [hoja de cálculo](./{ARCHIVOS['xlsx']}) "
      f"y una [presentación](./{ARCHIVOS['pptx']}).*\n")
    A("---\n")

    A("## Índice\n")
    for i, k in enumerate(["partida", "metodo", "seguridad", "estadia", "mov_donde", "mov_cuanto",
                           "lecturas", "reco", "confirmar"], 1):
        A(f"{i}. [{SEC[k]}](#{_slug(SEC[k])})")
    A("\n---\n")

    A(f"## {SEC['partida']}\n")
    A("Siete personas, tres noches, una ciudad que premia al que planea. Del viernes 30 de octubre al lunes 2 de "
      "noviembre de 2026 —fin de semana de Halloween, con Cali en su punto más salsero y más lleno—. El vuelo de "
      "ida sale de Cartagena a las 6 de la tarde y **aterriza a las 8 de la noche del 30**; el regreso es en el "
      "vuelo de las 9 de la noche del 2. La pregunta no es cómo llegar, sino cómo movernos por la ciudad y dónde "
      "dormir sin que el presupuesto ni la seguridad cedan.\n")
    A(f"El margen es explícito: **{cop(c['meta_min'])} a {cop(c['meta_max'])} por persona** entre transporte y "
      f"estadía, con licencia de estirar hasta **{cop(c['techo'])}** cuando la calidad lo amerite. Y una "
      "condición innegociable: la seguridad va primero. Después, lo que hace memorable un viaje —piscina para el "
      "calor, aire para la noche, cocina para no dejar el sueldo en restaurantes, y la rumba a pie.\n")
    A("> **Nota de la v2:** el cambio de horario de la ida (antes llegábamos de mañana) no toca la estadía; "
      "reordena solo la movilidad —para mejor en costo y con un cuidado nuevo por la llegada nocturna—.\n")

    A(f"## {SEC['metodo']}\n")
    A("Esto se armó como un pequeño proyecto de datos, no a ojo. El orden importa:\n")
    A("1. **Primero la vara, después la búsqueda.** Se fijaron los pesos de cada criterio —con la seguridad "
      "mandando— antes de mirar un solo precio.")
    A("2. **Precios reales, no de folleto.** Un navegador automatizado (Playwright) recorrió Hostelworld con las "
      "fechas exactas y siete huéspedes; el transporte se cotizó contra Kayak y agencias locales de Cali.")
    A("3. **Un puntaje propio y auditable** para la estadía (se explica abajo), separado de la calificación de "
      "huéspedes de las plataformas.")
    A("4. **Una sola fuente de datos** genera estos cuatro documentos: si un número cambia, los cuatro se "
      "actualizan en coherencia.\n")

    A(f"## {SEC['seguridad']}\n")
    A("Cali se lee por barrios. Donde el viajero duerme tranquilo y amanece cerca de todo: **"
      + ", ".join(ZONAS_SEGURAS) + "**. San Antonio —casas de colores, cuestas empedradas, salsa en cada "
      "esquina— es el favorito por razón. Lo que conviene esquivar: **" + ", ".join(ZONAS_EVITAR) + "**; la "
      "última es la subida al oeste alto, y suele ofrecerse disfrazada de ganga con vista.\n")

    A(f"## {SEC['estadia']}\n")
    A("El **9.6 o 9.8** junto a cada hostal es la calificación de huéspedes de Hostelworld, un dato externo. La "
      "decisión no se apoyó en ese número: se construyó un puntaje propio, de 0 a 100, con una nota de 1 a 5 por "
      "criterio multiplicada por su peso.\n")
    A("| Criterio | Peso | Cómo se asigna la nota (1–5) |")
    A("|---|:--:|---|")
    A("| 🔒 Seguridad del barrio | 30% | Por zona (San Antonio / Granada / El Peñón = 5) |")
    A("| ✨ Amenidades y comodidad | 20% | Aire acondicionado +2, piscina +2, cocina +1 (tope 5) |")
    A("| 💰 Precio por persona | 20% | El más barato = 5; escala lineal hasta el más caro = 1 |")
    A("| 📍 Cercanía a zona turística | 12% | Qué tan a pie queda de lo turístico |")
    A("| 🅿️ Parqueadero | 10% | Disponibilidad estimada *(baja certeza)* |")
    A("| 🎉 Ambiente social | 8% | Facilidad para conocer gente |")
    sn = subnotas(MEJOR)
    ejemplo = " + ".join(f"{peso}×{sn[cl]:.2g}⁄5" for cl, _, peso in PESOS_ESTADIA)
    A(f"\n> **Fórmula:** puntaje = suma de (peso × nota⁄5). Con el líder, {MEJOR['nombre']}: "
      f"{ejemplo} = **{puntaje(MEJOR):.1f}/100**.\n")
    A("Ordenados por ese puntaje propio. La última columna es para juzgar con ojos propios:\n")
    A("| # | Hostal | Zona | Puntaje | Calificación huéspedes | Aire | Piscina | Estadía por persona (3 noches) | Ver |")
    A("|:--:|---|---|:--:|:--:|:--:|:--:|--:|:--:|")
    for i, e in enumerate(ESTADIA_RANK, 1):
        estrella = " ★" if e is MEJOR else ""
        A(f"| {i} | {e['nombre']}{estrella} | {e['zona']} | **{puntaje(e):.1f}** | {e['rating_hw'] or '—'} | "
          f"{'✔' if e['ac'] else '—'} | {'✔' if e['piscina'] else '—'} | {cop(_pp_estadia(e))} | "
          f"[link]({e['url']}) |")
    A("")
    for e in ESTADIA_RANK:
        A(f"- **[{e['nombre']}]({e['url']})** — {e['nota']}")
    A("")

    A(f"## {SEC['mov_donde']}\n")
    A(LLEGADA + "\n")
    A(TIMING + "\n")

    A(f"## {SEC['mov_cuanto']}\n")
    A("Como quieren salir de Cali con libertad, el carro propio tiene sentido. Aun así, estas son las tres "
      "formas de resolverlo, de la más cómoda a la más barata. Todas con costo todo-incluido por persona "
      "(grupo de 7, con gasolina y taxis donde aplican); la cifra dura de referencia es el 7 puestos de Kayak "
      "en el aeropuerto (3 días).\n")
    A("| Opción | Qué implica | Por persona | Comodidad | Ver |")
    A("|---|---|--:|---|:--:|")
    for m in MOVILIDAD:
        tag = " ★" if m["recomendado"] else ""
        A(f"| **{m['nombre']}**{tag} | {m['detalle']} | **{cop(m['pp'])}** | {m['flex']} | [ver]({m['url']}) |")
    A("")
    A(f"> {PALANCA}\n")
    A("**Vehículos de 7 puestos para las fechas** — lo que cambia según dónde se recoja (local vs mostrador):\n")
    A("| Vehículo (7 puestos) | Agencia | Tarifa (3 días) | Por persona | ¿Cuadra con la llegada? | Ver |")
    A("|---|---|---|--:|---|:--:|")
    for v in VEHICULOS:
        A(f"| {v['modelo']} | {v['agencia']} | {v['tarifa']} | {v['pp_txt']} | {v['fit']} | [ver]({v['url']}) |")
    A(f"\n> {VEHICULOS_NOTA}\n")
    A("**Cómo cambia el total** con el hostal recomendado (Viajero, "
      f"{cop(_pp_estadia(MEJOR))} por persona de estadía):\n")
    A("| Estadía + forma de moverse | Total por persona | En el bolsillo |")
    A("|---|--:|:--:|")
    for s in SENSIBILIDAD:
        tag = " ★" if s["mov"]["recomendado"] else ""
        A(f"| Viajero + {s['mov']['corto'].lower()}{tag} | **{cop(s['total'])}** | {s['estado']} |")
    A("")

    A(f"## {SEC['lecturas']}\n")
    A(f"Cada lectura combina un hostal con la movilidad recomendada ({MOV_RECO['corto'].lower()}, "
      f"{cop(TRANSPORTE_REF)} por persona). Con otra forma de moverse, el total se corre según la tabla de "
      "arriba.\n")
    A("| Lectura | Estadía | Total por persona | En el bolsillo |")
    A("|---|---|--:|:--:|")
    for p in PAQUETES:
        tag = " ★" if p["recomendado"] else ""
        A(f"| **{p['nombre']}**{tag} | [{p['estadia']}]({p['url']}) | **{cop(p['total_pp'])}** | {p['estado']} |")
    A("")

    A(f"## {SEC['reco']}\n")
    A(f"**{RECO['estadia']} (estadía) + carro propio entregado por una agencia local ≈ "
      f"{cop(RECO['total_pp'])} por persona.** El hostal responde que sí a cada exigencia a la vez —zona más "
      "segura y caminable, piscina, aire, bar y rumba a un costado, y las clases de salsa que resuelven eso de "
      "conocer gente—. Y el carro, con una agencia local (Farallones, WayCarCali) que lo entrega coordinando el "
      "vuelo, da la libertad que pidieron para salir de Cali **sin pelear con el horario del mostrador**.\n")
    A(f"Palancas según la prioridad: el **mostrador del aeropuerto** (Kayak) es algo más barato "
      f"({cop(_pp_estadia(MEJOR) + 180_000)}) pero cierra ~10 pm y aprieta con la llegada de noche; moverse "
      f"**sin carro propio** baja a {cop(_pp_estadia(MEJOR) + MOV_MIN)} (entra en meta), a cambio de menos "
      "libertad para las salidas de la ciudad.\n")

    A(f"## {SEC['confirmar']}\n")
    A("Las cartas boca arriba:\n")
    A("- **Estadía:** ¿el precio es por persona o por habitación? Se asumió por persona (lo prudente). Y "
      "confirmar capacidad para siete con camas mínimo cinco al abrir cada ficha.")
    A(f"- **Carro:** pedir cotización por WhatsApp a [Farallones]({FARALLONES_URL}) o "
      f"[WayCarCali]({WAYCAR_URL}) para la **entrega en el aeropuerto coordinando el vuelo de las 8 pm** y el "
      "total exacto de los 3 días. Si en cambio usan el mostrador (Kayak), reservar recogida fuera de horario "
      "(24 h de aviso) por si el vuelo se retrasa.")
    A("- **El reloj corre:** cuatro semanas y fin de semana de Halloween. Lo bueno se reserva primero.\n")
    A("---")
    A(f"*Documentos hermanos: {ARCHIVOS_REF}. Generados desde una única fuente de datos "
      f"(`src/generar_entregables.py`); cambiar un número regenera los cuatro en coherencia.*")

    (OUT / ARCHIVOS["md"]).write_text("\n".join(L), encoding="utf-8")
    print(f"✔ {ARCHIVOS['md']}")


# ══════════════════════════════ 2) EXCEL .XLSX ══════════════════════════════
def build_xlsx() -> None:
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    from openpyxl.utils import get_column_letter

    money = '#,##0" COP"'
    fill_head = PatternFill("solid", fgColor=PRIMARY)
    fill_accent = PatternFill("solid", fgColor=ACCENT)
    fill_alt = PatternFill("solid", fgColor=ALTROW)
    fill_reco = PatternFill("solid", fgColor=ACCENT_SOFT)
    f_title = Font(name="Calibri", size=20, bold=True, color=PRIMARY_DK)
    f_sub = Font(name="Calibri", size=11, color=MUTE)
    f_head = Font(name="Calibri", size=11, bold=True, color=WHITE)
    f_bold = Font(name="Calibri", size=11, bold=True, color=PRIMARY_DK)
    f_link = Font(name="Calibri", size=11, color=PRIMARY_DK, underline="single")
    thin = Side(style="thin", color=SOFTLINE)
    border = Border(left=thin, right=thin, top=thin, bottom=thin)
    center = Alignment(horizontal="center", vertical="center", wrap_text=True)
    left = Alignment(horizontal="left", vertical="center", wrap_text=True)

    wb = Workbook()

    def head_row(ws, row, headers):
        for j, h in enumerate(headers, 1):
            cell = ws.cell(row=row, column=j, value=h)
            cell.fill = fill_head; cell.font = f_head; cell.alignment = center; cell.border = border

    def linkcell(ws, row, col, url, text="ver"):
        cell = ws.cell(row=row, column=col, value=text)
        cell.hyperlink = url; cell.font = f_link; cell.alignment = center; cell.border = border

    # Resumen
    ws = wb.active; ws.title = "Resumen"; ws.sheet_view.showGridLines = False
    ws.merge_cells("A1:G1"); ws["A1"] = CONTEXTO["titulo"] + " · " + CONTEXTO["subtitulo"] + " (v2)"; ws["A1"].font = f_title
    ws.merge_cells("A2:G2")
    ws["A2"] = (f"{CONTEXTO['personas']} personas · {CONTEXTO['fechas']} · {CONTEXTO['horarios']} · "
                f"Meta {cop(CONTEXTO['meta_min'])}–{cop(CONTEXTO['meta_max'])} por persona (flex {cop(CONTEXTO['techo'])})")
    ws["A2"].font = f_sub; ws["A2"].alignment = left; ws.row_dimensions[2].height = 44
    r = 4
    ws.cell(row=r, column=1, value="CUATRO LECTURAS (estadía + carro local con entrega)").font = f_bold; r += 1
    head_row(ws, r, ["Lectura", "Estadía", "Estadía p/persona", "Movilidad p/persona", "Total p/persona", "Estado", "Ver"]); r += 1
    for i, p in enumerate(PAQUETES):
        vals = [p["nombre"] + (" ★" if p["recomendado"] else ""), p["estadia"],
                p["estadia_pp"], p["transporte_pp"], p["total_pp"], p["estado"]]
        for j, v in enumerate(vals, 1):
            cell = ws.cell(row=r, column=j, value=v)
            cell.border = border; cell.alignment = center if j >= 3 else left
            if j in (3, 4, 5):
                cell.number_format = money
            if p["recomendado"]:
                cell.fill = fill_reco
                if j == 5:
                    cell.font = f_bold
            elif i % 2 == 0:
                cell.fill = fill_alt
        linkcell(ws, r, 7, p["url"]); r += 1
    r += 1
    ws.cell(row=r, column=1, value="RECOMENDACIÓN").font = f_bold; r += 1
    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=7)
    cell = ws.cell(row=r, column=1,
                   value=f"{RECO['estadia']} + carro local con entrega coordinada ≈ {cop(RECO['total_pp'])} por persona")
    cell.fill = fill_accent; cell.font = Font(color=INK, bold=True, size=11); cell.alignment = left
    ws.row_dimensions[r].height = 30
    for j, w in enumerate([24, 24, 16, 17, 15, 10, 8], 1):
        ws.column_dimensions[get_column_letter(j)].width = w

    # Movilidad
    ws = wb.create_sheet("Movilidad"); ws.sheet_view.showGridLines = False
    ws.merge_cells("A1:E1"); ws["A1"] = "🌙 Movilidad — la llegada es de noche (v2)"; ws["A1"].font = f_title
    ws.merge_cells("A2:E2"); ws["A2"] = LLEGADA; ws["A2"].font = f_sub; ws["A2"].alignment = left; ws.row_dimensions[2].height = 70
    ws.merge_cells("A3:E3"); ws["A3"] = TIMING; ws["A3"].font = f_sub; ws["A3"].alignment = left; ws.row_dimensions[3].height = 58
    head_row(ws, 5, ["Opción", "Qué implica", "Por persona", "Comodidad", "Ver"])
    r = 6
    for i, m in enumerate(MOVILIDAD):
        vals = [m["nombre"] + (" ★" if m["recomendado"] else ""), m["detalle"], m["pp"], m["flex"]]
        for j, v in enumerate(vals, 1):
            cell = ws.cell(row=r, column=j, value=v)
            cell.border = border; cell.alignment = center if j == 3 else left
            if j == 3:
                cell.number_format = money
            if m["recomendado"]:
                cell.fill = fill_reco
            elif i % 2 == 0:
                cell.fill = fill_alt
        linkcell(ws, r, 5, m["url"]); r += 1
    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=5)
    ws.cell(row=r, column=1, value=PALANCA).font = f_sub; ws.cell(row=r, column=1).alignment = left
    ws.row_dimensions[r].height = 30; r += 2
    ws.cell(row=r, column=1, value="Si el hostal es el Viajero, el total por persona queda:").font = f_bold; r += 1
    head_row(ws, r, ["Forma de moverse", "Total por persona", "Estado", "", ""]); r += 1
    for s in SENSIBILIDAD:
        vals = [s["mov"]["nombre"], s["total"], s["estado"]]
        for j, v in enumerate(vals, 1):
            cell = ws.cell(row=r, column=j, value=v)
            cell.border = border; cell.alignment = center if j == 2 else left
            if j == 2:
                cell.number_format = money
            if s["mov"]["recomendado"]:
                cell.fill = fill_reco
        r += 1
    for j, w in enumerate([44, 50, 16, 40, 8], 1):
        ws.column_dimensions[get_column_letter(j)].width = w

    # Vehículos (7 puestos)
    ws = wb.create_sheet("Vehículos (7 puestos)"); ws.sheet_view.showGridLines = False
    ws.merge_cells("A1:E1"); ws["A1"] = "🚙 Vehículos de 7 puestos — local (entrega) vs mostrador (Kayak)"; ws["A1"].font = f_title
    ws.merge_cells("A2:E2"); ws["A2"] = VEHICULOS_NOTA; ws["A2"].font = f_sub; ws["A2"].alignment = left; ws.row_dimensions[2].height = 58
    head_row(ws, 4, ["Vehículo (7 puestos)", "Agencia", "Tarifa (3 días)", "Por persona", "¿Cuadra con la llegada?", "Ver"])
    r = 5
    for i, v in enumerate(VEHICULOS):
        vals = [v["modelo"], v["agencia"], v["tarifa"], v["pp_txt"], v["fit"]]
        for j, val in enumerate(vals, 1):
            cell = ws.cell(row=r, column=j, value=val)
            cell.border = border; cell.alignment = center if j == 4 else left
            if i % 2 == 0:
                cell.fill = fill_alt
        linkcell(ws, r, 6, v["url"])
        r += 1
    for j, w in enumerate([28, 22, 18, 14, 32, 8], 1):
        ws.column_dimensions[get_column_letter(j)].width = w

    # Puntaje (metodología)
    ws = wb.create_sheet("Puntaje (metodología)"); ws.sheet_view.showGridLines = False
    ws.merge_cells("A1:I1"); ws["A1"] = "🎯 Cómo se compone el puntaje de estadía (0–100)"; ws["A1"].font = f_title
    ws.merge_cells("A2:I2")
    ws["A2"] = ("Nota 1–5 por criterio × peso. El puntaje es propio; la 'calificación huéspedes' es de Hostelworld "
                "(externa). Fórmula: puntaje = suma de (peso × nota⁄5).")
    ws["A2"].font = f_sub; ws["A2"].alignment = left; ws.row_dimensions[2].height = 28
    head_row(ws, 4, ["Hostal"] + [f"{n} ({p}%)" for _, n, p in PESOS_ESTADIA] + ["PUNTAJE", "Calif. huéspedes"])
    r = 5
    for i, e in enumerate(ESTADIA_RANK):
        sn = subnotas(e)
        vals = [e["nombre"]] + [round(sn[cl], 2) for cl, _, _ in PESOS_ESTADIA] + [puntaje(e), e["rating_hw"] or "—"]
        for j, v in enumerate(vals, 1):
            cell = ws.cell(row=r, column=j, value=v)
            cell.border = border; cell.alignment = center if j > 1 else left
            if j == len(vals) - 1:
                cell.font = f_bold
            if e is MEJOR:
                cell.fill = fill_reco
            elif i % 2 == 0:
                cell.fill = fill_alt
        r += 1
    for j, w in enumerate([30, 12, 18, 12, 13, 10, 9, 11, 14], 1):
        ws.column_dimensions[get_column_letter(j)].width = w

    # Estadía (datos)
    ws = wb.create_sheet("Estadía (datos)"); ws.sheet_view.showGridLines = False
    ws.merge_cells("A1:H1"); ws["A1"] = "🏨 Estadía — candidatos scrapeados (Hostelworld, fechas reales)"; ws["A1"].font = f_title
    head_row(ws, 3, ["Hostal", "Zona", "Calif. huéspedes", "Privada desde/noche", "Aire", "Piscina", "Estadía por persona (3n)", "Ver"])
    r = 4
    for i, e in enumerate(ESTADIA_RANK):
        vals = [e["nombre"], e["zona"], e["rating_hw"] or "—", e["priv_noche"],
                "Sí" if e["ac"] else "No", "Sí" if e["piscina"] else "No", _pp_estadia(e)]
        for j, v in enumerate(vals, 1):
            cell = ws.cell(row=r, column=j, value=v)
            cell.border = border; cell.alignment = center if j != 1 else left
            if j in (4, 7):
                cell.number_format = money
            if i % 2 == 0:
                cell.fill = fill_alt
        linkcell(ws, r, 8, e["url"]); r += 1
    for j, w in enumerate([32, 18, 15, 20, 7, 9, 20, 8], 1):
        ws.column_dimensions[get_column_letter(j)].width = w

    # Una hoja por lectura
    for p in PAQUETES:
        est = p["estadia_obj"]
        ws = wb.create_sheet(p["nombre"][:28]); ws.sheet_view.showGridLines = False
        ws.merge_cells("A1:D1"); ws["A1"] = p["nombre"]; ws["A1"].font = f_title
        ws.merge_cells("A2:D2"); ws["A2"] = p["nota"]; ws["A2"].font = f_sub; ws["A2"].alignment = left
        ws.row_dimensions[2].height = 40
        head_row(ws, 4, ["Concepto", "Detalle", "Por persona", "Grupo (×7)"])
        filas = [("Estadía (3 noches)", p["estadia"], p["estadia_pp"], p["estadia_pp"] * 7),
                 ("Movilidad recomendada", MOV_RECO["corto"], p["transporte_pp"], p["transporte_pp"] * 7)]
        r = 5
        for i, (concepto, detalle, ppv, grp) in enumerate(filas):
            for j, v in enumerate([concepto, detalle, ppv, grp], 1):
                cell = ws.cell(row=r, column=j, value=v)
                cell.border = border; cell.alignment = left if j <= 2 else center
                if j >= 3:
                    cell.number_format = money
                if i % 2 == 0:
                    cell.fill = fill_alt
            r += 1
        for j, v in enumerate(["TOTAL", f"Estado: {p['estado']}", p["total_pp"], p["total_pp"] * 7], 1):
            cell = ws.cell(row=r, column=j, value=v)
            cell.fill = fill_reco if p["recomendado"] else fill_head
            cell.font = f_bold if p["recomendado"] else f_head
            cell.alignment = left if j <= 2 else center; cell.border = border
            if j >= 3:
                cell.number_format = money
        r += 2
        ws.cell(row=r, column=1, value="Puntaje").font = f_bold
        ws.cell(row=r, column=2, value=puntaje(est)).font = f_bold; r += 1
        ws.cell(row=r, column=1, value="Enlace"); linkcell(ws, r, 2, est["url"], est["url"]); r += 2
        for k, v in [("Calificación huéspedes", est["rating_hw"] or "—"), ("Aire acondicionado", "Sí" if est["ac"] else "No"),
                     ("Piscina", "Sí" if est["piscina"] else "No"), ("Cocina", "Sí" if est["cocina"] else "No"),
                     ("Zona", est["zona"])]:
            ws.cell(row=r, column=1, value=k).alignment = left
            ws.cell(row=r, column=2, value=v).alignment = left
            r += 1
        for j, w in enumerate([26, 40, 16, 16], 1):
            ws.column_dimensions[get_column_letter(j)].width = w

    ws = wb["Resumen"]; last = ws.max_row + 2
    ws.merge_cells(start_row=last, start_column=1, end_row=last, end_column=7)
    ws.cell(row=last, column=1, value=f"Documentos hermanos: {ARCHIVOS['md']} · {ARCHIVOS['pdf']} · {ARCHIVOS['pptx']}").font = f_sub

    wb.save(OUT / ARCHIVOS["xlsx"])
    print(f"✔ {ARCHIVOS['xlsx']}")


# ══════════════════════════════ 3) PDF ══════════════════════════════
def build_pdf() -> None:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import cm
    from reportlab.platypus import (Image, KeepTogether, Paragraph, SimpleDocTemplate, Spacer,
                                    Table, TableStyle)

    c_primary = colors.HexColor("#" + PRIMARY)
    c_primary_d = colors.HexColor("#" + PRIMARY_DK)
    c_accent = colors.HexColor("#" + ACCENT)
    c_reco = colors.HexColor("#" + ACCENT_SOFT)
    c_alt = colors.HexColor("#" + ALTROW)
    c_ink = colors.HexColor("#" + INK)
    c_bg = colors.HexColor("#" + BG)
    c_line = colors.HexColor("#" + SOFTLINE)

    styles = getSampleStyleSheet()
    h1 = ParagraphStyle("h1", parent=styles["Title"], textColor=c_primary_d, fontSize=22, spaceAfter=2, alignment=0)
    sub = ParagraphStyle("sub", parent=styles["Normal"], textColor=colors.HexColor("#" + MUTE), fontSize=9)
    body = ParagraphStyle("body", parent=styles["Normal"], fontSize=9.6, leading=14, textColor=c_ink)
    pillst = ParagraphStyle("pillst", parent=styles["Normal"], fontSize=11.5, textColor=colors.white, leading=13)
    small = ParagraphStyle("small", parent=styles["Normal"], fontSize=8, textColor=colors.HexColor("#" + MUTE))
    cell = ParagraphStyle("cell", parent=body, fontSize=8.2, leading=10)
    cellb = ParagraphStyle("cellb", parent=cell, fontName="Helvetica-Bold")
    USABLE = 17.2 * cm

    def pill(text):
        w = min(USABLE, 0.8 * cm + len(text) * 0.235 * cm)
        t = Table([[Paragraph(f"<b>{text}</b>", pillst)]], colWidths=[w]); t.hAlign = "LEFT"
        t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), c_primary), ("ROUNDEDCORNERS", [7, 7, 7, 7]),
                               ("LEFTPADDING", (0, 0), (-1, -1), 11), ("RIGHTPADDING", (0, 0), (-1, -1), 11),
                               ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
        return t

    def card(flow, bg, border=None, radius=9):
        t = Table([[flow]], colWidths=[USABLE])
        st = [("BACKGROUND", (0, 0), (-1, -1), bg), ("ROUNDEDCORNERS", [radius] * 4),
              ("LEFTPADDING", (0, 0), (-1, -1), 13), ("RIGHTPADDING", (0, 0), (-1, -1), 13),
              ("TOPPADDING", (0, 0), (-1, -1), 11), ("BOTTOMPADDING", (0, 0), (-1, -1), 11)]
        if border:
            st.append(("BOX", (0, 0), (-1, -1), 1.3, border))
        t.setStyle(TableStyle(st))
        return t

    def _bg(canvas, docu):
        canvas.saveState(); canvas.setFillColor(c_bg)
        canvas.rect(0, 0, A4[0], A4[1], fill=1, stroke=0); canvas.restoreState()

    def tabla_datos(data, colw, destacar_reco):
        tbl = Table(data, colWidths=colw)
        st = [("BACKGROUND", (0, 0), (-1, 0), c_primary), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
              ("FONTSIZE", (0, 0), (-1, -1), 8.4), ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
              ("BOX", (0, 0), (-1, -1), 0.4, c_line), ("LINEBELOW", (0, 0), (-1, -1), 0.3, c_line),
              ("ALIGN", (1, 1), (-1, -1), "CENTER"), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
              ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
              ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, c_alt])]
        for i, flag in enumerate(destacar_reco, 1):
            if flag:
                st.append(("BACKGROUND", (0, i), (-1, i), c_reco))
        tbl.setStyle(TableStyle(st))
        return tbl

    doc = SimpleDocTemplate(str(OUT / ARCHIVOS["pdf"]), pagesize=A4,
                            leftMargin=1.9 * cm, rightMargin=1.9 * cm, topMargin=1.1 * cm, bottomMargin=1.0 * cm)
    E = []
    flag_imgs = []
    if FLAG_CTG.exists():
        flag_imgs.append(Image(str(FLAG_CTG), width=1.55 * cm, height=0.93 * cm))
    if FLAG_CALI.exists():
        flag_imgs.append(Image(str(FLAG_CALI), width=1.55 * cm, height=1.03 * cm))
    if len(flag_imgs) == 2:
        fl = Table([[flag_imgs[0], Paragraph("→", body), flag_imgs[1]]], colWidths=[1.85 * cm, 0.6 * cm, 1.85 * cm])
        fl.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                                ("BACKGROUND", (0, 0), (-1, -1), colors.white), ("ROUNDEDCORNERS", [8, 8, 8, 8]),
                                ("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                                ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
        left_cell = fl
    else:
        left_cell = flag_imgs[0] if flag_imgs else Paragraph("", body)
    head = Table([[left_cell, Paragraph(f"<b>{CONTEXTO['titulo']}</b><br/>{CONTEXTO['subtitulo']}", h1)]],
                 colWidths=[5.0 * cm, 11.8 * cm])
    head.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
    E.append(head)
    E.append(Paragraph(f"Resumen ejecutivo · {CONTEXTO['fecha_informe']} · planeación v2 · "
                       f"{CONTEXTO['personas']} personas · {CONTEXTO['fechas']}", sub))
    E.append(Spacer(1, 0.3 * cm))

    E.append(pill("El encargo")); E.append(Spacer(1, 0.12 * cm))
    E.append(card(Paragraph(
        f"Siete personas, tres noches en Cali (30 oct – 2 nov, fin de semana de Halloween). La ida sale 6:00 pm "
        f"del 30 y <b>llega 8:00 pm</b>; el regreso es en el vuelo de las 9:00 pm del 2. Se resuelve la "
        f"movilización local y la estadía por {cop(CONTEXTO['meta_min'])}–{cop(CONTEXTO['meta_max'])} por persona "
        f"(flex {cop(CONTEXTO['techo'])}), con la seguridad como condición innegociable. Esta es la <b>v2</b>: el "
        "cambio de horario reordena solo la movilidad.", body), colors.white))
    E.append(Spacer(1, 0.22 * cm))

    E.append(pill("La recomendación")); E.append(Spacer(1, 0.12 * cm))
    E.append(card(Paragraph(
        f"<b>{RECO['estadia']} + carro propio entregado por una agencia local ≈ {cop(RECO['total_pp'])} "
        "por persona.</b> El hostal cumple todo (seguridad, piscina, aire, bar, rumba a pie y salsa para conocer "
        "gente); una agencia local (Farallones, WayCarCali) entrega el carro coordinando el vuelo, que es lo que "
        f"cuadra con la llegada de las 8 pm. El mostrador del aeropuerto es algo más barato "
        f"({cop(_pp_estadia(MEJOR) + 180_000)}) pero cierra ~10 pm; sin carro propio baja a "
        f"{cop(_pp_estadia(MEJOR) + MOV_MIN)}.", body), c_reco, border=c_accent))
    E.append(Spacer(1, 0.22 * cm))

    E.append(pill("La llegada es de noche")); E.append(Spacer(1, 0.12 * cm))
    E.append(card(Paragraph(LLEGADA, body), colors.white))
    E.append(Spacer(1, 0.22 * cm))

    data = [["Opción", "Por persona", "Comodidad"]]
    for m in MOVILIDAD:
        st = cellb if m["recomendado"] else cell
        data.append([Paragraph(m["nombre"] + (" ★" if m["recomendado"] else ""), st), cop(m["pp"]),
                     Paragraph(m["flex"], st)])
    E.append(KeepTogether([pill("Cómo moverse — tres opciones (por persona)"), Spacer(1, 0.12 * cm),
                           tabla_datos(data, [5.2 * cm, 2.2 * cm, 7.6 * cm], [m["recomendado"] for m in MOVILIDAD])]))
    E.append(Spacer(1, 0.08 * cm)); E.append(Paragraph(PALANCA, small))
    E.append(Spacer(1, 0.22 * cm))

    data = [["Lectura", "Estadía", "Total por persona", "Estado"]]
    for p in PAQUETES:
        data.append([p["nombre"] + (" ★" if p["recomendado"] else ""), p["estadia"], cop(p["total_pp"]), p["estado"]])
    E.append(KeepTogether([pill("Cuatro lecturas del presupuesto"), Spacer(1, 0.12 * cm),
                           tabla_datos(data, [3.8 * cm, 5.2 * cm, 3.2 * cm, 2.2 * cm], [p["recomendado"] for p in PAQUETES])]))
    E.append(Spacer(1, 0.22 * cm))

    E.append(pill("Para revisar cada opción")); E.append(Spacer(1, 0.12 * cm))
    hlinks = [f'<link href="{e["url"]}"><font color="#{PRIMARY_DK}">{e["nombre"].split(" (")[0]}</font></link>'
              for e in ESTADIA_RANK]
    E.append(card([Paragraph("<b>Estadía:</b>  " + " · ".join(hlinks), body), Spacer(1, 0.1 * cm),
                   Paragraph('<b>Carro:</b>  '
                             f'<link href="{FARALLONES_URL}"><font color="#{PRIMARY_DK}">Farallones</font></link> · '
                             f'<link href="{WAYCAR_URL}"><font color="#{PRIMARY_DK}">WayCarCali</font></link> · '
                             f'<link href="{KAYAK_URL}"><font color="#{PRIMARY_DK}">Kayak (aeropuerto)</font></link> · '
                             f'<link href="{TAXI_URL}"><font color="#{PRIMARY_DK}">tarifas de taxi</font></link>', body)],
                  c_reco))
    E.append(Spacer(1, 0.15 * cm))
    E.append(Paragraph(
        f"Parte de un paquete: {ARCHIVOS['md']} · {ARCHIVOS['xlsx']} · {ARCHIVOS['pptx']}. Estadía asumida por "
        "persona/noche; movilidad todo-incluido estimada. Reservar pronto: fin de semana de Halloween.", small))

    doc.build(E, onFirstPage=_bg, onLaterPages=_bg)
    print(f"✔ {ARCHIVOS['pdf']}")


# ══════════════════════════════ 4) PPTX ══════════════════════════════
def build_pptx() -> None:
    from pptx import Presentation
    from pptx.chart.data import CategoryChartData
    from pptx.dml.color import RGBColor
    from pptx.enum.chart import XL_CHART_TYPE
    from pptx.enum.shapes import MSO_SHAPE
    from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
    from pptx.oxml.ns import qn
    from pptx.util import Inches, Pt

    C_PRIM = RGBColor.from_string(PRIMARY)
    C_PRIM_D = RGBColor.from_string(PRIMARY_DK)
    C_ACC = RGBColor.from_string(ACCENT)
    C_BG = RGBColor.from_string(BG)
    C_INK = RGBColor.from_string(INK)
    C_MUTE = RGBColor.from_string(MUTE)
    C_WHITE = RGBColor.from_string(WHITE)
    # tintes suaves para las tarjetas
    T_PEACH, T_SAGE, T_ROSE, T_SKY, T_SAND = "F6E7D6", "E6EDDC", "F4E0DA", "E1E9EB", ALTROW
    GRIS_BAR = "D8C4B2"

    prs = Presentation()
    prs.slide_width = Inches(13.333); prs.slide_height = Inches(7.5)
    blank = prs.slide_layouts[6]

    def fondo(slide, color=C_BG):
        slide.background.fill.solid(); slide.background.fill.fore_color.rgb = color

    def _sombra(shape, alpha=32000):
        sp = shape._element.spPr
        for el in sp.findall(qn("a:effectLst")):
            sp.remove(el)
        eff = sp.makeelement(qn("a:effectLst"), {})
        shd = sp.makeelement(qn("a:outerShdw"),
                             {"blurRad": "95000", "dist": "40000", "dir": "5400000", "rotWithShape": "0"})
        clr = sp.makeelement(qn("a:srgbClr"), {"val": "6E5B4E"})
        clr.append(sp.makeelement(qn("a:alpha"), {"val": str(alpha)}))
        shd.append(clr); eff.append(shd); sp.append(eff)

    def tarjeta(slide, x, y, w, h, fill=WHITE, line=None, radius=0.12, sombra=True):
        sh = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
        try:
            sh.adjustments[0] = radius
        except Exception:
            pass
        sh.fill.solid(); sh.fill.fore_color.rgb = RGBColor.from_string(fill)
        if line:
            sh.line.color.rgb = RGBColor.from_string(line); sh.line.width = Pt(2)
        else:
            sh.line.fill.background()
        if sombra:
            _sombra(sh)
        return sh

    def _round_pic(pic, radius=9000):
        spPr = pic._element.spPr
        geom = spPr.find(qn("a:prstGeom"))
        if geom is None:
            geom = spPr.makeelement(qn("a:prstGeom"), {}); spPr.append(geom)
        geom.set("prst", "roundRect")
        for ch in list(geom):
            geom.remove(ch)
        avLst = geom.makeelement(qn("a:avLst"), {})
        avLst.append(geom.makeelement(qn("a:gd"), {"name": "adj", "fmla": f"val {radius}"}))
        geom.append(avLst)

    def circulo(slide, x, y, d, fill, emoji, esz=26, ecol=None):
        ov = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x), Inches(y), Inches(d), Inches(d))
        ov.fill.solid(); ov.fill.fore_color.rgb = RGBColor.from_string(fill); ov.line.fill.background()
        tf = ov.text_frame; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
        r = p.add_run(); r.text = emoji; r.font.size = Pt(esz); r.font.color.rgb = ecol or C_INK
        return ov

    def bloque(slide, x, y, w, h, items, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP):
        tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
        tf = tb.text_frame; tf.word_wrap = True; tf.vertical_anchor = anchor
        for k, (t, sz, col, bold) in enumerate(items):
            p = tf.paragraphs[0] if k == 0 else tf.add_paragraph()
            p.alignment = align
            r = p.add_run(); r.text = t; r.font.size = Pt(sz); r.font.bold = bold; r.font.color.rgb = col
        return tb

    def header(slide, emoji, titulo):
        tarjeta(slide, 0.4, 0.3, 12.53, 0.82, fill=PRIMARY, radius=0.5)
        bloque(slide, 0.85, 0.3, 11.8, 0.82, [(f"{emoji}   {titulo}", 24, C_WHITE, True)], anchor=MSO_ANCHOR.MIDDLE)

    def pill(slide, x, y, w, h, text, fill, tcol, sz=12):
        tarjeta(slide, x, y, w, h, fill=fill, radius=0.5, sombra=False)
        bloque(slide, x, y, w, h, [(text, sz, tcol, True)], align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

    def chart_barras(slide, x, y, w, h, cats, vals, destacado_idx=None):
        cd = CategoryChartData(); cd.categories = cats; cd.add_series("v", vals)
        gx = slide.shapes.add_chart(XL_CHART_TYPE.BAR_CLUSTERED, Inches(x), Inches(y), Inches(w), Inches(h), cd).chart
        gx.has_legend = False
        ser = gx.plots[0].series[0]
        for idx in range(len(vals)):
            pt = ser.points[idx]; pt.format.fill.solid()
            pt.format.fill.fore_color.rgb = C_ACC if idx == destacado_idx else RGBColor.from_string(GRIS_BAR)
        return gx

    # ── 1 portada ──
    s = prs.slides.add_slide(blank); fondo(s)
    tarjeta(s, 4.2, 0.55, 4.93, 1.72, fill=WHITE, radius=0.22)
    if FLAG_CTG.exists():
        p = s.shapes.add_picture(str(FLAG_CTG), Inches(4.78), Inches(0.72), height=Inches(0.92)); _round_pic(p)
    bloque(s, 6.42, 0.9, 0.9, 0.6, [("→", 26, C_PRIM, True)], align=PP_ALIGN.CENTER)
    if FLAG_CALI.exists():
        p = s.shapes.add_picture(str(FLAG_CALI), Inches(7.22), Inches(0.72), height=Inches(0.92)); _round_pic(p)
    bloque(s, 4.2, 1.72, 4.93, 0.42, [("de Cartagena a Cali", 12, C_MUTE, False)], align=PP_ALIGN.CENTER)
    tarjeta(s, 1.3, 2.95, 10.73, 3.5, fill=WHITE, radius=0.07)
    bloque(s, 1.6, 3.25, 10.1, 1.1, [(CONTEXTO["titulo"], 46, C_PRIM_D, True)], align=PP_ALIGN.CENTER)
    bloque(s, 1.6, 4.45, 10.1, 0.5, [(CONTEXTO["subtitulo"], 18, C_MUTE, False)], align=PP_ALIGN.CENTER)
    pill(s, 6.17, 5.05, 1.0, 0.42, "v2", ACCENT, C_INK, sz=13)
    bloque(s, 1.6, 5.6, 10.1, 0.8,
           [(f"{CONTEXTO['personas']} personas    ·    {CONTEXTO['fechas']}", 14, C_INK, False),
            (CONTEXTO["horarios"], 12, C_MUTE, False)], align=PP_ALIGN.CENTER)

    # ── 2 punto de partida (tarjetas) ──
    s = prs.slides.add_slide(blank); fondo(s); header(s, "🧭", "Punto de partida")
    datos2 = [("👥", "El grupo", "7 personas · 3 noches", T_PEACH),
              ("🗓️", "Las fechas", "30 oct – 2 nov · llega 8 pm", T_SAGE),
              ("💰", "El presupuesto", "$300–400k p/p · flex $480k", T_ROSE),
              ("🔒", "La prioridad", "Seguridad, siempre primero", T_SKY)]
    for (emoji, lab, val, tint), (x, y) in zip(datos2, [(0.6, 1.5), (6.83, 1.5), (0.6, 4.0), (6.83, 4.0)]):
        tarjeta(s, x, y, 5.9, 2.2, fill=WHITE)
        circulo(s, x + 0.4, y + 0.55, 1.1, ACCENT_SOFT, emoji, esz=32)
        bloque(s, x + 1.75, y + 0.5, 3.9, 1.3,
               [(lab, 14, C_MUTE, True), (val, 19, C_INK, True)], anchor=MSO_ANCHOR.MIDDLE)

    # ── 3 cómo se hizo (4 pasos en tarjetas) ──
    s = prs.slides.add_slide(blank); fondo(s); header(s, "🧪", "Cómo se hizo esto")
    pasos = [("La vara primero", "Pesos de cada criterio (seguridad al frente) antes de ver un solo precio."),
             ("Precios reales", "Un robot recorrió Hostelworld con las fechas reales; el transporte, contra Kayak y locales."),
             ("Puntaje propio", "Nota de 1 a 5 por criterio × su peso, auditable; aparte del rating externo."),
             ("Una sola fuente", "Los mismos datos generan los 4 documentos: cambiar un número los actualiza todos.")]
    for i, (tit, txt) in enumerate(pasos):
        x = 0.5 + i * 3.1
        tarjeta(s, x, 1.65, 2.95, 4.6, fill=WHITE)
        circulo(s, x + 1.05, 2.0, 0.85, ACCENT, str(i + 1), esz=26, ecol=C_WHITE)
        bloque(s, x + 0.2, 3.0, 2.55, 3.1,
               [(tit, 16, C_PRIM_D, True), ("", 6, C_INK, False), (txt, 12.5, C_INK, False)])

    # ── 4 cómo se puntuó (6 criterios en tarjetas) ──
    s = prs.slides.add_slide(blank); fondo(s); header(s, "🎯", "Cómo se puntuó la estadía")
    bloque(s, 0.6, 1.3, 12.1, 0.7,
           [("La calificación de huéspedes (9.6, 9.8…) es externa. El puntaje 0–100 es propio: "
             "nota 1–5 por criterio × su peso.   Puntaje = suma de (peso × nota⁄5).", 14, C_INK, False)])
    _nombres = ["Seguridad del barrio", "Amenidades y comodidad", "Precio por persona",
                "Cercanía a zona turística", "Parqueadero", "Ambiente social"]
    _reglas = ["Por zona (San Antonio / Granada = 5)", "Aire +2, piscina +2, cocina +1", "Más barato = 5; lineal al más caro",
               "Qué tan a pie de lo turístico", "Disponibilidad estimada (baja certeza)", "Facilidad para conocer gente"]
    _pesos = [p for _, _, p in PESOS_ESTADIA]
    _emojis = ["🔒", "✨", "💰", "📍", "🅿️", "🎉"]
    for i in range(6):
        x = 0.55 + (i % 3) * 4.08
        y = 2.25 + (i // 3) * 2.15
        tarjeta(s, x, y, 3.9, 1.95, fill=WHITE)
        bloque(s, x + 0.2, y + 0.18, 1.35, 1.62,
               [(_emojis[i], 26, C_INK, False), (f"{_pesos[i]}%", 27, C_ACC, True)],
               align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        bloque(s, x + 1.6, y + 0.25, 2.2, 1.5,
               [(_nombres[i], 14, C_PRIM_D, True), (_reglas[i], 11.5, C_MUTE, False)], anchor=MSO_ANCHOR.MIDDLE)

    # ── 5 estadía finalistas (gráfico en tarjeta) ──
    s = prs.slides.add_slide(blank); fondo(s); header(s, "🏨", "Estadía — los finalistas")
    tarjeta(s, 0.5, 1.45, 8.3, 5.4, fill=WHITE, radius=0.05)
    cats = [e["nombre"].split(" (")[0].replace(" Hostel", "").replace(" & Salsa School", "") for e in ESTADIA_RANK]
    chart_barras(s, 0.75, 1.6, 7.9, 5.1, cats, [puntaje(e) for e in ESTADIA_RANK], destacado_idx=ESTADIA_RANK.index(MEJOR))
    tarjeta(s, 9.05, 1.8, 3.85, 3.6, fill=ACCENT_SOFT)
    bloque(s, 9.35, 2.1, 3.3, 3.1,
           [(f"★ {MEJOR['nombre'].split(' (')[0]}", 17, C_PRIM_D, True),
            (f"lidera con {puntaje(MEJOR):.1f}/100.", 15, C_INK, False), ("", 8, C_INK, False),
            ("Puntaje propio (seguridad, amenidades, precio, cercanía, parqueo, social), no el rating externo.",
             13, C_INK, False)], anchor=MSO_ANCHOR.MIDDLE)

    # ── 5b estadía — comparación (tabla) ──
    s = prs.slides.add_slide(blank); fondo(s); header(s, "🏨", "Estadía — comparación")
    bloque(s, 0.6, 1.25, 12.1, 0.5,
           [("Ordenadas por nuestro puntaje. 'Por persona' = las 3 noches. Toca 'ver' para revisar cada una.", 14, C_INK, False)])
    _cabe = ["Hostal", "Zona", "Puntaje", "Precio/noche", "Por persona (3n)", "Ver"]
    tabla = s.shapes.add_table(len(ESTADIA_RANK) + 1, 6, Inches(0.5), Inches(1.9), Inches(12.33), Inches(4.5)).table
    for w, ancho in zip(range(6), [Inches(3.9), Inches(2.2), Inches(1.4), Inches(1.95), Inches(1.98), Inches(0.9)]):
        tabla.columns[w].width = ancho
    for j, h in enumerate(_cabe):
        c0 = tabla.cell(0, j); c0.text = h; c0.fill.solid(); c0.fill.fore_color.rgb = C_PRIM
        rr = c0.text_frame.paragraphs[0].runs[0]; rr.font.bold = True; rr.font.color.rgb = C_WHITE; rr.font.size = Pt(12)
    for i, e in enumerate(ESTADIA_RANK, 1):
        precio_noche = "—" if e["nombre"].startswith("Casa/Apto") else cop(e["priv_noche"])
        fila = [e["nombre"].split(" (")[0] + (" ★" if e is MEJOR else ""), e["zona"], f"{puntaje(e):.1f}",
                precio_noche, cop(_pp_estadia(e)), "ver"]
        for j, val in enumerate(fila):
            cl = tabla.cell(i, j); cl.text = val
            para = cl.text_frame.paragraphs[0]; rr = para.runs[0]
            rr.font.size = Pt(11); rr.font.color.rgb = C_INK
            if j in (2, 3, 4, 5):
                para.alignment = PP_ALIGN.CENTER
            if j == 5:
                rr.font.color.rgb = C_PRIM_D; rr.font.underline = True; rr.hyperlink.address = e["url"]
            cl.fill.solid()
            cl.fill.fore_color.rgb = (RGBColor.from_string(ACCENT_SOFT) if e is MEJOR
                                      else (C_WHITE if i % 2 else RGBColor.from_string(ALTROW)))

    # ── 6 la llegada es de noche (3 tarjetas) ──
    s = prs.slides.add_slide(blank); fondo(s); header(s, "🌙", "La llegada es de noche")
    noche = [("🕘", "3 días limpios", "Recoger esa noche y devolver ~7 pm del 2: por debajo de las 72 h."),
             ("✅", "Local = cuadra", "Farallones / WayCarCali entregan el carro coordinando el vuelo de las 8 pm."),
             ("⚠️", "Mostrador = ojo", "Alamo / Localiza: más baratos, pero cierran ~10 pm. Reservar fuera de horario (24 h).")]
    for i, (emoji, tit, txt) in enumerate(noche):
        x = 0.55 + i * 4.08
        destacada = (i == 1)
        tarjeta(s, x, 1.65, 3.9, 3.9, fill=WHITE, line=(ACCENT if destacada else None))
        circulo(s, x + 1.45, 2.0, 1.0, ACCENT_SOFT, emoji, esz=30)
        bloque(s, x + 0.3, 3.15, 3.3, 2.3,
               [(tit, 18, C_PRIM_D, True), ("", 6, C_INK, False), (txt, 13.5, C_INK, False)], align=PP_ALIGN.CENTER)
    bloque(s, 0.6, 5.8, 12.1, 0.6,
           [("Red de seguridad: los taxis oficiales del aeropuerto operan 24/7 (distintivo amarillo, tarifados).",
             13, C_MUTE, False)], align=PP_ALIGN.CENTER)

    # ── 7 cómo moverse — tres opciones (3 tarjetas) ──
    s = prs.slides.add_slide(blank); fondo(s); header(s, "🚗", "Cómo moverse — tres opciones")
    opciones = [("Carro local (entrega)", MOV_RECO["pp"], "Cuadra con la llegada de noche; libertad para salir de Cali.", True),
                ("Mostrador (Kayak)", 180_000, "Más barato, pero el mostrador cierra ~10 pm.", False),
                ("Sin carro propio", MOV_MIN, "Lo más barato: taxis + una van con conductor para el paseo.", False)]
    for i, (tit, pp, txt, reco) in enumerate(opciones):
        x = 0.55 + i * 4.08
        tarjeta(s, x, 1.7, 3.9, 4.5, fill=(ACCENT_SOFT if reco else WHITE), line=(ACCENT if reco else None))
        if reco:
            pill(s, x + 1.1, 1.45, 1.7, 0.5, "★ Recomendado", ACCENT, C_INK, sz=12)
        bloque(s, x + 0.3, 2.1, 3.3, 0.8, [(tit, 18, C_PRIM_D, True)], align=PP_ALIGN.CENTER)
        bloque(s, x + 0.3, 3.0, 3.3, 1.1,
               [(cop(pp), 34, C_ACC, True), ("por persona", 13, C_MUTE, False)], align=PP_ALIGN.CENTER)
        bloque(s, x + 0.35, 4.45, 3.2, 1.6, [(txt, 13.5, C_INK, False)], align=PP_ALIGN.CENTER)

    # ── 7b opciones de vehículo (tabla) ──
    s = prs.slides.add_slide(blank); fondo(s); header(s, "🚙", "Opciones de vehículo (7 puestos)")
    bloque(s, 0.6, 1.2, 12.1, 0.55,
           [("Lo que cambia según dónde se recoja: local (entrega, cuadra con la llegada) vs mostrador "
             "(más barato, horario rígido).", 13, C_INK, False)])
    _cab = ["Vehículo (7 puestos)", "Agencia", "Tarifa (3 días)", "Por persona", "¿Cuadra con la llegada?", "Ver"]
    tabla = s.shapes.add_table(len(VEHICULOS) + 1, 6, Inches(0.4), Inches(1.85), Inches(12.5), Inches(4.0)).table
    for w, ancho in zip(range(6), [Inches(2.7), Inches(2.15), Inches(2.0), Inches(1.75), Inches(3.1), Inches(0.8)]):
        tabla.columns[w].width = ancho
    for j, h in enumerate(_cab):
        c0 = tabla.cell(0, j); c0.text = h; c0.fill.solid(); c0.fill.fore_color.rgb = C_PRIM
        rr = c0.text_frame.paragraphs[0].runs[0]; rr.font.bold = True; rr.font.color.rgb = C_WHITE; rr.font.size = Pt(11)
    for i, v in enumerate(VEHICULOS, 1):
        local = v["fit"].startswith("Sí")
        fila = [v["modelo"], v["agencia"], v["tarifa"], v["pp_txt"], v["fit"], "ver"]
        for j, val in enumerate(fila):
            cl = tabla.cell(i, j); cl.text = val
            para = cl.text_frame.paragraphs[0]; rr = para.runs[0]
            rr.font.size = Pt(10.5); rr.font.color.rgb = C_INK
            if j == 3:
                para.alignment = PP_ALIGN.CENTER
            if j == 5:
                para.alignment = PP_ALIGN.CENTER
                rr.font.color.rgb = C_PRIM_D; rr.font.underline = True; rr.hyperlink.address = v["url"]
            cl.fill.solid()
            cl.fill.fore_color.rgb = (RGBColor.from_string(ACCENT_SOFT) if local else RGBColor.from_string("EFE6DA"))
    bloque(s, 0.5, 6.1, 12.4, 1.2, [(VEHICULOS_NOTA, 11.5, C_PRIM_D, False)])

    # ── 8 recomendación (hero) ──
    s = prs.slides.add_slide(blank); fondo(s)
    bloque(s, 0.8, 0.5, 11.7, 0.9, [("🏆  La recomendación", 34, C_PRIM_D, True)], align=PP_ALIGN.CENTER)
    tarjeta(s, 1.4, 1.75, 10.53, 2.5, fill=WHITE, line=ACCENT, radius=0.1)
    bloque(s, 1.7, 2.0, 9.9, 1.9,
           [(f"{RECO['estadia']}  +  carro local (entrega coordinada)", 21, C_INK, True),
            ("", 8, C_INK, False), (f"≈ {cop(RECO['total_pp'])} por persona", 30, C_PRIM_D, True)],
           align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    alts = [(f"Mostrador (Kayak): {cop(_pp_estadia(MEJOR) + 180_000)}", T_SAND),
            (f"Sin carro propio: {cop(_pp_estadia(MEJOR) + MOV_MIN)} (en meta)", T_SAGE),
            (f"En meta de estadía: Patio del Río {cop(PAQUETES[1]['total_pp'])}", T_PEACH)]
    for i, (txt, tint) in enumerate(alts):
        x = 0.9 + i * 3.95
        tarjeta(s, x, 4.6, 3.7, 1.5, fill=WHITE)
        bloque(s, x + 0.25, 4.6, 3.2, 1.5, [(txt, 14, C_INK, True)], align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    bloque(s, 0.8, 6.4, 11.7, 0.6,
           [("El hostal dice sí a todo (seguridad, piscina, aire, bar, rumba y salsa); el carro local da libertad "
             "sin pelear con el horario.", 13, C_MUTE, False)], align=PP_ALIGN.CENTER)

    # ── 9 antes de reservar (checklist en tarjetas + links) ──
    s = prs.slides.add_slide(blank); fondo(s); header(s, "📋", "Antes de reservar")
    checks = ["Estadía: ¿precio por persona o por habitación? Y capacidad para 7 (camas ≥5).",
              "Carro: cotizar por WhatsApp la entrega en el aeropuerto coordinando el vuelo de las 8 pm, y el total de 3 días.",
              "Si usan el mostrador (Kayak): reservar recogida fuera de horario (24 h) por si el vuelo se retrasa.",
              "Reservar pronto: cuatro semanas y fin de semana de Halloween."]
    for i, txt in enumerate(checks):
        x = 0.6 + (i % 2) * 6.25
        y = 1.55 + (i // 2) * 1.75
        tarjeta(s, x, y, 5.95, 1.55, fill=WHITE)
        circulo(s, x + 0.3, y + 0.42, 0.72, T_SAGE, "✓", esz=24, ecol=RGBColor.from_string("5B7D4F"))
        bloque(s, x + 1.3, y + 0.18, 4.5, 1.25, [(txt, 13, C_INK, False)], anchor=MSO_ANCHOR.MIDDLE)
    tarjeta(s, 0.6, 5.2, 12.1, 1.5, fill=ACCENT_SOFT)
    tb = s.shapes.add_textbox(Inches(0.95), Inches(5.35), Inches(11.5), Inches(1.3)); tf = tb.text_frame; tf.word_wrap = True
    p0 = tf.paragraphs[0]; run = p0.add_run(); run.text = "Estadía:  "
    run.font.size = Pt(13); run.font.bold = True; run.font.color.rgb = C_PRIM_D
    for e in ESTADIA_RANK:
        run = p0.add_run(); run.text = e["nombre"].split(" (")[0] + "   "
        run.font.size = Pt(12); run.font.color.rgb = C_PRIM_D; run.font.underline = True; run.hyperlink.address = e["url"]
    p1 = tf.add_paragraph(); run = p1.add_run(); run.text = "Agencias:  "
    run.font.size = Pt(13); run.font.bold = True; run.font.color.rgb = C_PRIM_D
    for nombre, url in [("Farallones", FARALLONES_URL), ("WayCarCali", WAYCAR_URL), ("Car Rent", CARRENT_URL),
                        ("Kayak (aeropuerto)", KAYAK_URL)]:
        run = p1.add_run(); run.text = nombre + "   "
        run.font.size = Pt(12); run.font.color.rgb = C_PRIM_D; run.font.underline = True; run.hyperlink.address = url
    bloque(s, 0.6, 6.95, 12.1, 0.4, [(f"Documentos hermanos: {ARCHIVOS_REF}", 10, C_MUTE, False)])

    prs.save(OUT / ARCHIVOS["pptx"])
    print(f"✔ {ARCHIVOS['pptx']}")


def _normalizar_flags() -> None:
    try:
        from PIL import Image
        for src, dst in [(ASSETS / "flag_cali.png", FLAG_CALI), (ASSETS / "flag_cartagena.png", FLAG_CTG)]:
            if src.exists():
                Image.open(src).convert("RGB").save(dst)
    except Exception as e:
        print(f"  (aviso: no se pudieron normalizar las banderas: {e})")


def main() -> None:
    OUT.mkdir(exist_ok=True); ASSETS.mkdir(exist_ok=True)
    _normalizar_flags()
    build_md(); build_xlsx(); build_pdf(); build_pptx()
    print("\n✔ 4/4 entregables regenerados (v2: movilidad reajustada a la llegada de noche)")


if __name__ == "__main__":
    main()
