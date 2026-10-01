"""
generar_entregables.py — Fuente única de datos + generador de los 4 entregables (v5).

v5: se reincorpora el ÍNDICE y la sección de METODOLOGÍA al informe; la movilidad se
explica en lenguaje llano (respuesta directa a "¿el carro en el aeropuerto o en la
ciudad?") y se retiran las siglas (S1/S2…, CLO). Datos de transporte anclados a Kayak
(7 puestos en el aeropuerto) y a agencias locales con entrega en el aeropuerto.

Produce en output/: informe_completo.md, resumen_ejecutivo.pdf,
resumen_resultados.xlsx, presentacion_cali_2026.pptx (se referencian entre sí).
Correr:  uv run python src/generar_entregables.py
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
    "horarios": "Salida 30 oct 7:00 am de Cartagena · regreso en vuelo 9:00 pm del 2 nov",
    "origen": "Cartagena — llegada en avión (Aeropuerto Alfonso Bonilla Aragón)",
    "meta_min": 300_000,
    "meta_max": 400_000,
    "techo": 480_000,
    "fecha_informe": "30 de septiembre de 2026",
}

# ─────────────── LINKS ───────────────
KAYAK_URL = ("https://www.kayak.com.co/cars/Santiago-de-Cali,Colombia-c11092/2026-10-30/2026-11-02;map"
             "?fs=carcapacity=precise_7;carlocationid=~CLO&ucs=9x1xcq&sort=rank_a")
FARALLONES_URL = "https://farallonesrentacar.com/listavehiculos/"
WAYCAR_URL = "https://waycarcali.com/"
CARRENT_URL = "https://carrent.com.co/alquiler-de-van-en-cali"
TAXI_URL = "https://www.taxislibres.com.co/blog/tarifas-taxi-cali-decreto-1084-2025"

# ─────────────── ESTADÍA (scrapeado + evaluado) ───────────────
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

# ─────────────── MOVILIDAD (opciones en lenguaje llano, todo incluido por persona) ───────────────
AEROPUERTO = ("En el aeropuerto, sin dudarlo. No hay que elegir entre barato y cómodo: hay agencias locales "
              "—más económicas que las marcas grandes— que o tienen oficina en el propio aeropuerto (Farallones) "
              "o llevan el carro hasta allá sin costo cuando el alquiler es de 3 días o más (WayCarCali). Se "
              "aterriza, se recoge el carro ahí mismo y se devuelve en el aeropuerto antes de volar. Ir hasta la "
              "ciudad a buscarlo solo agregaría un taxi y tiempo, sin ahorrar nada.")

TIMING = ("Un detalle de horarios: el alquiler se cobra por días de 24 horas desde que se recoge, con una hora de "
          "gracia. Como se llega la mañana del 30 y se vuela a las 9 de la noche del 2, conservar el carro hasta "
          "esa noche cruza a un cuarto día de alquiler. Vale la pena: ese último tramo —entre dejar el hostal al "
          "mediodía y el vuelo de la noche— es justo cuando más sirve el carro, con las maletas ya encima. Si se "
          "devuelve de noche, conviene avisar a la agencia con un día de anticipación.")

MOVILIDAD = [
    {"nombre": "Carro propio todo el viaje, recogido en el aeropuerto", "pp": 150_000,
     "detalle": "Una van de 7 puestos de agencia local, recogida y devuelta en el mismo aeropuerto, manejándola "
                "ustedes, con la gasolina ya contada.",
     "flex": "La más cómoda: carro desde que aterrizan hasta que abordan, y libertad para salir de Cali cuando "
             "quieran (Pance, Calima).",
     "url": FARALLONES_URL, "recomendado": True},
    {"nombre": "Carro propio, pero solo tres días", "pp": 140_000,
     "detalle": "Se devuelve al mediodía del último día para no pagar el cuarto día; esa última tarde se mueven "
                "en taxi, ya con las maletas.",
     "flex": "Ahorro pequeño; la última tarde quedan sin carro y cargando maletas.",
     "url": KAYAK_URL, "recomendado": False},
    {"nombre": "Sin carro propio: taxis y una van con conductor para el paseo de afuera", "pp": 125_000,
     "detalle": "Taxis y apps dentro de la ciudad, más una van con conductor contratada solo para el día que "
                "salgan de Cali.",
     "flex": "La más barata y sin manejar ni parquear; a cambio, menos libertad para salir de improviso.",
     "url": CARRENT_URL, "recomendado": False},
]
MOV_RECO = next(m for m in MOVILIDAD if m["recomendado"])
TRANSPORTE_REF = MOV_RECO["pp"]
MOV_MIN = min(m["pp"] for m in MOVILIDAD)
MOSTRADOR_GRANDE = 235_000  # referencia: mostrador de marcas grandes en el aeropuerto (innecesario)

ZONAS_SEGURAS = ["San Antonio", "Granada", "El Peñón", "Santa Teresita", "Ciudad Jardín"]
ZONAS_EVITAR = ["Aguablanca (oriente)", "Siloé", "Terrón Colorado (ladera oeste alta)"]

BASE = "Mini-Boom-en-Cali"  # base de los nombres de archivo
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


# ─────────────── SCORING ───────────────
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

# Títulos de sección (para mantener índice y encabezados en sincronía)
SEC = {
    "partida": "Punto de partida",
    "metodo": "Cómo se hizo esto",
    "seguridad": "Geografía de la seguridad",
    "estadia": "Estadía: el puntaje y los finalistas",
    "mov_donde": "Movilidad: ¿en el aeropuerto o en la ciudad?",
    "mov_cuanto": "Movilidad: cuánto carro llevar",
    "lecturas": "Cuatro lecturas del presupuesto",
    "reco": "La recomendación",
    "confirmar": "Lo que queda por confirmar",
}


# ══════════════════════════════ 1) INFORME .MD ══════════════════════════════
def build_md() -> None:
    c = CONTEXTO
    L: list[str] = []
    A = L.append

    A(f"# {c['titulo']}")
    A(f"### {c['subtitulo']}\n")
    A("![Cartagena](./assets/flag_cartagena.png) → ![Cali](./assets/flag_cali.png)  ")
    A("*De Cartagena a Cali.*\n")
    A(f"*Informe completo · {c['fecha_informe']}. Lo acompañan un [resumen ejecutivo](./{ARCHIVOS['pdf']}), "
      f"una [hoja de cálculo](./{ARCHIVOS['xlsx']}) y una [presentación](./{ARCHIVOS['pptx']}).*\n")
    A("---\n")

    # Índice
    A("## Índice\n")
    for i, k in enumerate(["partida", "metodo", "seguridad", "estadia", "mov_donde", "mov_cuanto",
                           "lecturas", "reco", "confirmar"], 1):
        A(f"{i}. [{SEC[k]}](#{_slug(SEC[k])})")
    A("\n---\n")

    A(f"## {SEC['partida']}\n")
    A("Siete personas, tres noches, una ciudad que premia al que planea. Del viernes 30 de octubre al lunes 2 de "
      "noviembre de 2026 —fin de semana de Halloween, con Cali en su punto más salsero y más lleno—. Se sale de "
      "Cartagena a las 7:00 am del 30 y se regresa en el vuelo de las 9:00 pm del 2: la pregunta no es cómo "
      "llegar, sino cómo movernos por la ciudad y dónde dormir sin que el presupuesto ni la seguridad cedan.\n")
    A(f"El margen es explícito: **{cop(c['meta_min'])} a {cop(c['meta_max'])} por persona** entre transporte y "
      f"estadía, con licencia de estirar hasta **{cop(c['techo'])}** cuando la calidad lo amerite. Y una "
      "condición innegociable: la seguridad va primero. Después, lo que hace memorable un viaje —piscina para el "
      "calor, aire para la noche, cocina para no dejar el sueldo en restaurantes, y la rumba a pie.\n")

    A(f"## {SEC['metodo']}\n")
    A("Esto se armó como un pequeño proyecto de datos, no a ojo. El orden importa:\n")
    A("1. **Primero la vara, después la búsqueda.** Se fijaron los pesos de cada criterio —con la seguridad "
      "mandando— antes de mirar un solo precio, para no dejarse llevar por la primera opción bonita.")
    A("2. **Precios reales, no de folleto.** Un navegador automatizado (Playwright) recorrió Hostelworld con las "
      "fechas exactas y siete huéspedes; el transporte se cotizó contra la búsqueda real de Kayak y contra "
      "agencias locales de Cali.")
    A("3. **Un puntaje propio y auditable** para la estadía (se explica más abajo), separado de la calificación "
      "de huéspedes de las plataformas.")
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
    A("| Seguridad del barrio | 30% | Por zona (San Antonio / Granada / El Peñón = 5) |")
    A("| Amenidades y comodidad | 20% | Aire acondicionado +2, piscina +2, cocina +1 (tope 5) |")
    A("| Precio por persona | 20% | El más barato = 5; escala lineal hasta el más caro = 1 |")
    A("| Cercanía a zona turística | 12% | Qué tan a pie queda de lo turístico |")
    A("| Parqueadero | 10% | Disponibilidad estimada *(baja certeza)* |")
    A("| Ambiente social | 8% | Facilidad para conocer gente |")
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
    A("**" + AEROPUERTO + "**\n")
    A(TIMING + "\n")

    A(f"## {SEC['mov_cuanto']}\n")
    A("Resuelto el *dónde*, queda el *cuánto*: tres formas de moverse, de la más cómoda a la más barata. Todas "
      "con costo todo-incluido por persona (grupo de 7, con gasolina y taxis donde aplican).\n")
    A("| Opción | Qué implica | Por persona | Comodidad | Ver |")
    A("|---|---|--:|---|:--:|")
    for m in MOVILIDAD:
        tag = " ★" if m["recomendado"] else ""
        A(f"| **{m['nombre']}**{tag} | {m['detalle']} | **{cop(m['pp'])}** | {m['flex']} | [ver]({m['url']}) |")
    A("")
    A(f"> El mostrador de las marcas grandes en el aeropuerto costaría casi el doble (~{cop(MOSTRADOR_GRANDE)} por "
      "persona): con las agencias locales que entregan allá mismo, no hace falta.\n")
    A("**Cómo cambia el total** con el hostal recomendado (Viajero, "
      f"{cop(_pp_estadia(MEJOR))} por persona de estadía):\n")
    A("| Estadía + forma de moverse | Total por persona | En el bolsillo |")
    A("|---|--:|:--:|")
    for s in SENSIBILIDAD:
        tag = " ★" if s["mov"]["recomendado"] else ""
        A(f"| Viajero + {s['mov']['nombre'].split(',')[0].split(':')[0].lower()}{tag} | **{cop(s['total'])}** | {s['estado']} |")
    A("")

    A(f"## {SEC['lecturas']}\n")
    A(f"Cada lectura combina un hostal con la movilidad recomendada ({MOV_RECO['nombre']}, "
      f"{cop(TRANSPORTE_REF)} por persona). Con otra forma de moverse, el total se corre según la tabla de "
      "arriba.\n")
    A("| Lectura | Estadía | Total por persona | En el bolsillo |")
    A("|---|---|--:|:--:|")
    for p in PAQUETES:
        tag = " ★" if p["recomendado"] else ""
        A(f"| **{p['nombre']}**{tag} | [{p['estadia']}]({p['url']}) | **{cop(p['total_pp'])}** | {p['estado']} |")
    A("")

    A(f"## {SEC['reco']}\n")
    A(f"**{RECO['estadia']} (estadía) + carro propio todo el viaje recogido en el aeropuerto ≈ "
      f"{cop(RECO['total_pp'])} por persona.** El hostal responde que sí a cada exigencia a la vez —zona más "
      "segura y caminable, piscina, aire, bar y rumba a un costado, y las clases de salsa que resuelven eso de "
      "conocer gente—. Y la movilidad recomendada da carro todos los días sin vueltas a la ciudad ni hueco final "
      "con maletas, más barato que el mostrador de las marcas grandes.\n")
    A(f"Palancas según la prioridad: si manda el ahorro, moverse **sin carro propio** baja el total a "
      f"{cop(_pp_estadia(MEJOR) + MOV_MIN)} (entra en meta), a cambio de menos libertad para salir de Cali; si "
      f"lo que pesa es no pasar de 400 mil en estadía, **[Hostal Patio del Río]({PAQUETES[1]['url']})** "
      f"({cop(PAQUETES[1]['total_pp'])}) mantiene piscina y aire.\n")

    A(f"## {SEC['confirmar']}\n")
    A("Las cartas boca arriba:\n")
    A("- **Estadía:** ¿el precio es por persona o por habitación? Se asumió por persona (lo prudente). Y "
      "confirmar capacidad para siete con camas mínimo cinco al abrir cada ficha.")
    A(f"- **Movilidad:** una llamada por WhatsApp a [Farallones]({FARALLONES_URL}) o "
      f"[WayCarCali]({WAYCAR_URL}) para cerrar la van de 7 puestos en las fechas, confirmar la entrega en el "
      "aeropuerto y el precio del cuarto día.")
    A("- **El reloj corre:** cinco semanas y fin de semana de Halloween. Lo bueno se reserva primero.\n")
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
    ws.merge_cells("A1:G1"); ws["A1"] = CONTEXTO["titulo"] + " · " + CONTEXTO["subtitulo"]; ws["A1"].font = f_title
    ws.merge_cells("A2:G2")
    ws["A2"] = (f"{CONTEXTO['personas']} personas · {CONTEXTO['fechas']} · {CONTEXTO['horarios']} · "
                f"Meta {cop(CONTEXTO['meta_min'])}–{cop(CONTEXTO['meta_max'])} por persona (flex {cop(CONTEXTO['techo'])})")
    ws["A2"].font = f_sub; ws["A2"].alignment = left; ws.row_dimensions[2].height = 30
    r = 4
    ws.cell(row=r, column=1, value="CUATRO LECTURAS (estadía + carro propio todo el viaje)").font = f_bold; r += 1
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
                   value=f"{RECO['estadia']} + carro propio todo el viaje (recogido en el aeropuerto) ≈ {cop(RECO['total_pp'])} por persona")
    cell.fill = fill_accent; cell.font = Font(color=INK, bold=True, size=11); cell.alignment = left
    ws.row_dimensions[r].height = 30
    for j, w in enumerate([24, 24, 16, 17, 15, 10, 8], 1):
        ws.column_dimensions[get_column_letter(j)].width = w

    # Movilidad
    ws = wb.create_sheet("Movilidad"); ws.sheet_view.showGridLines = False
    ws.merge_cells("A1:E1"); ws["A1"] = "Movilidad — ¿en el aeropuerto o en la ciudad?"; ws["A1"].font = f_title
    ws.merge_cells("A2:E2"); ws["A2"] = AEROPUERTO; ws["A2"].font = f_sub; ws["A2"].alignment = left; ws.row_dimensions[2].height = 58
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
    ws.cell(row=r, column=1, value=f"Mostrador de marcas grandes en el aeropuerto (referencia, innecesario)")
    ws.cell(row=r, column=3, value=MOSTRADOR_GRANDE).number_format = money; r += 2
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

    # Puntaje (metodología)
    ws = wb.create_sheet("Puntaje (metodología)"); ws.sheet_view.showGridLines = False
    ws.merge_cells("A1:I1"); ws["A1"] = "Cómo se compone el puntaje de estadía (0–100)"; ws["A1"].font = f_title
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
    ws.merge_cells("A1:H1"); ws["A1"] = "Estadía — candidatos scrapeados (Hostelworld, fechas reales)"; ws["A1"].font = f_title
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
                 ("Movilidad recomendada", MOV_RECO["nombre"], p["transporte_pp"], p["transporte_pp"] * 7)]
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
    from reportlab.platypus import (Image, Paragraph, SimpleDocTemplate, Spacer,
                                    Table, TableStyle)

    c_primary = colors.HexColor("#" + PRIMARY)
    c_primary_d = colors.HexColor("#" + PRIMARY_DK)
    c_reco = colors.HexColor("#" + ACCENT_SOFT)
    c_alt = colors.HexColor("#" + ALTROW)
    c_ink = colors.HexColor("#" + INK)

    styles = getSampleStyleSheet()
    h1 = ParagraphStyle("h1", parent=styles["Title"], textColor=c_primary_d, fontSize=22, spaceAfter=2, alignment=0)
    sub = ParagraphStyle("sub", parent=styles["Normal"], textColor=colors.HexColor("#" + MUTE), fontSize=9)
    h2 = ParagraphStyle("h2", parent=styles["Heading2"], textColor=c_primary, fontSize=13, spaceBefore=7, spaceAfter=2)
    body = ParagraphStyle("body", parent=styles["Normal"], fontSize=9.4, leading=13.5, textColor=c_ink)
    small = ParagraphStyle("small", parent=styles["Normal"], fontSize=8, textColor=colors.HexColor("#" + MUTE))
    cell = ParagraphStyle("cell", parent=body, fontSize=8.2, leading=10)
    cellb = ParagraphStyle("cellb", parent=cell, fontName="Helvetica-Bold")

    doc = SimpleDocTemplate(str(OUT / ARCHIVOS["pdf"]), pagesize=A4,
                            leftMargin=1.9 * cm, rightMargin=1.9 * cm, topMargin=1.1 * cm, bottomMargin=1.0 * cm)
    E = []
    flag_imgs = []
    if FLAG_CTG.exists():
        flag_imgs.append(Image(str(FLAG_CTG), width=1.7 * cm, height=1.02 * cm))
    if FLAG_CALI.exists():
        flag_imgs.append(Image(str(FLAG_CALI), width=1.7 * cm, height=1.13 * cm))
    if len(flag_imgs) == 2:
        fl = Table([[flag_imgs[0], Paragraph("→", body), flag_imgs[1]]], colWidths=[1.8 * cm, 0.6 * cm, 1.8 * cm])
        fl.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("ALIGN", (0, 0), (-1, -1), "CENTER")]))
        left_cell = fl
    else:
        left_cell = flag_imgs[0] if flag_imgs else Paragraph("", body)
    head = Table([[left_cell, Paragraph(f"<b>{CONTEXTO['titulo']}</b><br/>{CONTEXTO['subtitulo']}", h1)]],
                 colWidths=[4.6 * cm, 12 * cm])
    head.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
    E.append(head)
    E.append(Paragraph(f"Resumen ejecutivo · {CONTEXTO['fecha_informe']} · {CONTEXTO['personas']} personas · "
                       f"{CONTEXTO['fechas']} · de Cartagena a Cali", sub))
    E.append(Spacer(1, 0.25 * cm))

    E.append(Paragraph("El encargo", h2))
    E.append(Paragraph(
        f"Siete personas, tres noches en Cali (30 oct – 2 nov, fin de semana de Halloween). Salida 7:00 am del 30 "
        f"desde Cartagena; regreso en el vuelo de las 9:00 pm del 2. Se resuelve la movilización local y la "
        f"estadía por {cop(CONTEXTO['meta_min'])}–{cop(CONTEXTO['meta_max'])} por persona (flex "
        f"{cop(CONTEXTO['techo'])}), con la seguridad como condición innegociable. Método: criterios primero, "
        "precios reales (Hostelworld y Kayak), un puntaje propio para la estadía y una sola fuente de datos "
        "para los cuatro documentos.", body))

    E.append(Paragraph("La recomendación", h2))
    E.append(Paragraph(
        f"<b>{RECO['estadia']} + carro propio todo el viaje, recogido en el aeropuerto ≈ {cop(RECO['total_pp'])} "
        "por persona.</b> El hostal cumple todo (seguridad, piscina, aire, bar, rumba a pie y salsa para conocer "
        "gente); la movilidad recomendada da carro todos los días sin vueltas a la ciudad ni hueco final con "
        f"maletas. Ahorro máximo moviéndose sin carro propio: {cop(_pp_estadia(MEJOR) + MOV_MIN)}.", body))

    E.append(Paragraph("¿El carro en el aeropuerto o en la ciudad?", h2))
    E.append(Paragraph("<b>En el aeropuerto.</b> " + AEROPUERTO.split("sin dudarlo. ")[1], body))

    E.append(Paragraph("Cómo moverse — tres opciones (por persona)", h2))
    data = [["Opción", "Por persona", "Comodidad"]]
    for m in MOVILIDAD:
        st = cellb if m["recomendado"] else cell
        data.append([Paragraph(m["nombre"] + (" ★" if m["recomendado"] else ""), st), cop(m["pp"]),
                     Paragraph(m["flex"], st)])
    tbl = Table(data, colWidths=[5.2 * cm, 2.2 * cm, 7.6 * cm])
    tstyle = [("BACKGROUND", (0, 0), (-1, 0), c_primary), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
              ("FONTSIZE", (0, 0), (-1, -1), 8.2), ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
              ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#" + SOFTLINE)),
              ("ALIGN", (1, 1), (1, -1), "CENTER"), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
              ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, c_alt])]
    for i, m in enumerate(MOVILIDAD, 1):
        if m["recomendado"]:
            tstyle.append(("BACKGROUND", (0, i), (-1, i), c_reco))
    tbl.setStyle(TableStyle(tstyle))
    E.append(tbl)
    E.append(Spacer(1, 0.1 * cm))
    E.append(Paragraph(
        "El carro se cobra por días de 24 horas desde que se recoge. Conservarlo hasta el vuelo de la noche del "
        "último día suma un cuarto día, pero cubre el tramo entre dejar el hostal y volar, con las maletas "
        "encima. El mostrador de las marcas grandes costaría casi el doble: no hace falta.", small))

    E.append(Paragraph("Cuatro lecturas del presupuesto (estadía + carro propio todo el viaje)", h2))
    data = [["Lectura", "Estadía", "Total por persona", "Estado"]]
    for p in PAQUETES:
        data.append([p["nombre"] + (" ★" if p["recomendado"] else ""), p["estadia"], cop(p["total_pp"]), p["estado"]])
    tbl = Table(data, colWidths=[3.8 * cm, 5.2 * cm, 3.2 * cm, 2.2 * cm])
    tstyle = [("BACKGROUND", (0, 0), (-1, 0), c_primary), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
              ("FONTSIZE", (0, 0), (-1, -1), 8.5), ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
              ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#" + SOFTLINE)),
              ("ALIGN", (2, 1), (-1, -1), "CENTER"), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
              ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, c_alt])]
    for i, p in enumerate(PAQUETES, 1):
        if p["recomendado"]:
            tstyle += [("BACKGROUND", (0, i), (-1, i), c_reco), ("FONTNAME", (0, i), (-1, i), "Helvetica-Bold")]
    tbl.setStyle(TableStyle(tstyle))
    E.append(tbl)

    E.append(Paragraph("Para revisar cada opción", h2))
    hlinks = [f'<link href="{e["url"]}"><font color="#{PRIMARY_DK}">{e["nombre"].split(" (")[0]}</font></link>'
              for e in ESTADIA_RANK]
    E.append(Paragraph("Estadía: " + " · ".join(hlinks), body))
    E.append(Paragraph(
        f'Carro: <link href="{FARALLONES_URL}"><font color="#{PRIMARY_DK}">Farallones</font></link> · '
        f'<link href="{WAYCAR_URL}"><font color="#{PRIMARY_DK}">WayCarCali</font></link> · '
        f'<link href="{KAYAK_URL}"><font color="#{PRIMARY_DK}">Kayak (aeropuerto)</font></link> · '
        f'<link href="{TAXI_URL}"><font color="#{PRIMARY_DK}">tarifas de taxi</font></link>', body))
    E.append(Paragraph(
        f"Parte de un paquete: {ARCHIVOS['md']} · {ARCHIVOS['xlsx']} · {ARCHIVOS['pptx']}. Estadía asumida por "
        "persona/noche; movilidad todo-incluido estimada. Reservar pronto: fin de semana de Halloween.", small))

    doc.build(E)
    print(f"✔ {ARCHIVOS['pdf']}")


# ══════════════════════════════ 4) PPTX ══════════════════════════════
def build_pptx() -> None:
    from pptx import Presentation
    from pptx.chart.data import CategoryChartData
    from pptx.dml.color import RGBColor
    from pptx.enum.chart import XL_CHART_TYPE
    from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
    from pptx.util import Inches, Pt

    C_PRIM = RGBColor.from_string(PRIMARY)
    C_PRIM_D = RGBColor.from_string(PRIMARY_DK)
    C_ACC = RGBColor.from_string(ACCENT)
    C_BG = RGBColor.from_string(BG)
    C_INK = RGBColor.from_string(INK)
    C_MUTE = RGBColor.from_string(MUTE)
    C_WHITE = RGBColor.from_string(WHITE)

    prs = Presentation()
    prs.slide_width = Inches(13.333); prs.slide_height = Inches(7.5)
    SW = prs.slide_width
    blank = prs.slide_layouts[6]

    def fondo(slide, color):
        slide.background.fill.solid(); slide.background.fill.fore_color.rgb = color

    def caja(slide, x, y, w, h, texto, size=18, color=None, bold=False, align=PP_ALIGN.LEFT):
        tb = slide.shapes.add_textbox(x, y, w, h); tf = tb.text_frame; tf.word_wrap = True
        for k, linea in enumerate(texto.split("\n")):
            p = tf.paragraphs[0] if k == 0 else tf.add_paragraph()
            p.alignment = align
            run = p.add_run(); run.text = linea
            run.font.size = Pt(size); run.font.bold = bold
            run.font.color.rgb = color or C_INK
        return tb

    def barra_titulo(slide, texto):
        sh = slide.shapes.add_shape(1, 0, 0, SW, Inches(1.05))
        sh.fill.solid(); sh.fill.fore_color.rgb = C_PRIM; sh.line.fill.background()
        tf = sh.text_frame; tf.word_wrap = True; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = tf.paragraphs[0]; r = p.add_run(); r.text = "   " + texto
        r.font.size = Pt(26); r.font.bold = True; r.font.color.rgb = C_WHITE

    # 1 portada
    s = prs.slides.add_slide(blank); fondo(s, C_BG)
    if FLAG_CTG.exists():
        s.shapes.add_picture(str(FLAG_CTG), Inches(4.35), Inches(0.7), height=Inches(1.15))
    caja(s, Inches(6.05), Inches(0.95), Inches(1.1), Inches(0.6), "→", 30, C_PRIM, True, PP_ALIGN.CENTER)
    if FLAG_CALI.exists():
        s.shapes.add_picture(str(FLAG_CALI), Inches(7.2), Inches(0.7), height=Inches(1.15))
    caja(s, Inches(3.5), Inches(1.95), Inches(6.33), Inches(0.4), "de Cartagena a Cali", 13, C_MUTE, False, PP_ALIGN.CENTER)
    banda = s.shapes.add_shape(1, 0, Inches(3.2), SW, Inches(1.4))
    banda.fill.solid(); banda.fill.fore_color.rgb = C_PRIM; banda.line.fill.background()
    caja(s, Inches(0.8), Inches(3.35), Inches(11.7), Inches(1.0), CONTEXTO["titulo"], 46, C_WHITE, True, PP_ALIGN.CENTER)
    caja(s, Inches(0.8), Inches(4.85), Inches(11.7), Inches(0.6), CONTEXTO["subtitulo"], 19, C_PRIM_D, False, PP_ALIGN.CENTER)
    caja(s, Inches(0.8), Inches(5.75), Inches(11.7), Inches(1.0),
         f"{CONTEXTO['personas']} personas   ·   {CONTEXTO['fechas']}\n{CONTEXTO['horarios']}",
         14, C_MUTE, False, PP_ALIGN.CENTER)

    # 2 punto de partida
    s = prs.slides.add_slide(blank); fondo(s, C_WHITE); barra_titulo(s, "Punto de partida")
    caja(s, Inches(0.9), Inches(1.5), Inches(11.5), Inches(5.2),
         ("Siete personas, tres noches, una ciudad que premia al que planea. Fin de semana de Halloween.\n\n"
          "Salida 7:00 am del 30 desde Cartagena; regreso en el vuelo de las 9:00 pm del 2. El reto no es\n"
          "llegar, sino movernos por Cali y dónde dormir.\n\n"
          f"Margen: {cop(CONTEXTO['meta_min'])}–{cop(CONTEXTO['meta_max'])} por persona (flex "
          f"{cop(CONTEXTO['techo'])}). Condición innegociable: la seguridad primero.\n"
          "Después: piscina, aire, cocina y rumba a distancia de caminar."), 20, C_INK)

    # 3 cómo se hizo (metodología)
    s = prs.slides.add_slide(blank); fondo(s, C_WHITE); barra_titulo(s, "Cómo se hizo esto")
    caja(s, Inches(0.9), Inches(1.5), Inches(11.5), Inches(5.0),
         ("Un pequeño proyecto de datos, no a ojo:\n\n"
          "1. Primero la vara: los pesos de cada criterio (seguridad al frente) antes de ver un solo precio.\n"
          "2. Precios reales: un navegador automatizado recorrió Hostelworld con las fechas y siete huéspedes;\n"
          "     el transporte, contra Kayak y agencias locales.\n"
          "3. Un puntaje propio y auditable para la estadía, aparte de la calificación de huéspedes.\n"
          "4. Una sola fuente de datos genera los cuatro documentos: cambiar un número los actualiza todos."),
         19, C_INK)

    # 4 seguridad
    s = prs.slides.add_slide(blank); fondo(s, C_WHITE); barra_titulo(s, "Geografía de la seguridad")
    caja(s, Inches(0.9), Inches(1.5), Inches(5.6), Inches(0.6), "Donde sí", 22, RGBColor.from_string(POSITIVE), True)
    caja(s, Inches(0.9), Inches(2.2), Inches(5.6), Inches(4.0), "\n".join("•  " + z for z in ZONAS_SEGURAS), 18, C_INK)
    caja(s, Inches(7.0), Inches(1.5), Inches(5.4), Inches(0.6), "Donde no", 22, C_PRIM, True)
    caja(s, Inches(7.0), Inches(2.2), Inches(5.4), Inches(4.0), "\n".join("•  " + z for z in ZONAS_EVITAR), 18, C_INK)

    # 4b cómo se puntuó la estadía (criterios + pesos)
    s = prs.slides.add_slide(blank); fondo(s, C_WHITE); barra_titulo(s, "Cómo se puntuó la estadía")
    caja(s, Inches(0.9), Inches(1.25), Inches(11.5), Inches(1.1),
         ("La calificación de huéspedes (9.6, 9.8…) es un dato externo. El puntaje de 0 a 100 es propio:\n"
          "una nota de 1 a 5 por criterio, multiplicada por su peso.   Puntaje = suma de (peso × nota⁄5)."),
         16, C_INK)
    _nombres = ["Seguridad del barrio", "Amenidades y comodidad", "Precio por persona",
                "Cercanía a zona turística", "Parqueadero", "Ambiente social"]
    _reglas = ["Por zona (San Antonio / Granada / El Peñón = 5)", "Aire +2, piscina +2, cocina +1 (tope 5)",
               "El más barato = 5; lineal hasta el más caro = 1", "Qué tan a pie queda de lo turístico",
               "Disponibilidad estimada (baja certeza)", "Facilidad para conocer gente"]
    _pesos = [p for _, _, p in PESOS_ESTADIA]
    tabla = s.shapes.add_table(len(_nombres) + 1, 3, Inches(0.9), Inches(2.55), Inches(11.5), Inches(4.1)).table
    tabla.columns[0].width = Inches(4.3); tabla.columns[1].width = Inches(1.3); tabla.columns[2].width = Inches(5.9)
    for j, h in enumerate(["Criterio", "Peso", "Cómo se asigna la nota (de 1 a 5)"]):
        c0 = tabla.cell(0, j); c0.text = h; c0.fill.solid(); c0.fill.fore_color.rgb = C_PRIM
        rr = c0.text_frame.paragraphs[0].runs[0]; rr.font.bold = True; rr.font.color.rgb = C_WHITE; rr.font.size = Pt(14)
    for i in range(len(_nombres)):
        for j, v in enumerate([_nombres[i], f"{_pesos[i]}%", _reglas[i]]):
            cl = tabla.cell(i + 1, j); cl.text = v
            para = cl.text_frame.paragraphs[0]; rr = para.runs[0]
            rr.font.size = Pt(13); rr.font.color.rgb = C_INK
            if j == 1:
                rr.font.bold = True; para.alignment = PP_ALIGN.CENTER
            cl.fill.solid(); cl.fill.fore_color.rgb = C_WHITE if i % 2 == 0 else RGBColor.from_string(ALTROW)

    # 5 estadía finalistas
    s = prs.slides.add_slide(blank); fondo(s, C_WHITE); barra_titulo(s, "Estadía — los finalistas")
    cd = CategoryChartData()
    cd.categories = [e["nombre"].split(" (")[0].replace(" Hostel", "").replace(" & Salsa School", "") for e in ESTADIA_RANK]
    cd.add_series("Puntaje", [puntaje(e) for e in ESTADIA_RANK])
    gx = s.shapes.add_chart(XL_CHART_TYPE.BAR_CLUSTERED, Inches(0.7), Inches(1.4), Inches(8.4), Inches(5.4), cd).chart
    gx.has_legend = False
    ser = gx.plots[0].series[0]
    for idx, e in enumerate(ESTADIA_RANK):
        pt = ser.points[idx]; pt.format.fill.solid()
        pt.format.fill.fore_color.rgb = C_ACC if e is MEJOR else RGBColor.from_string("D8C4B2")
    caja(s, Inches(9.3), Inches(1.9), Inches(3.7), Inches(4.4),
         (f"{MEJOR['nombre'].split(' (')[0]} lidera con {puntaje(MEJOR):.1f}/100.\n\n"
          "Puntaje propio (seguridad 30%, amenidades, precio, cercanía, parqueo, social), no la calificación externa."),
         16, C_PRIM_D)

    # 6 movilidad — ¿aeropuerto o ciudad?
    s = prs.slides.add_slide(blank); fondo(s, C_WHITE); barra_titulo(s, "¿El carro en el aeropuerto o en la ciudad?")
    caja(s, Inches(0.9), Inches(1.4), Inches(11.5), Inches(1.1), "En el aeropuerto.", 30, C_PRIM_D, True)
    caja(s, Inches(0.9), Inches(2.6), Inches(11.5), Inches(4.0),
         ("No hay que elegir entre barato y cómodo. Hay agencias locales —más económicas que las marcas "
          "grandes— que tienen oficina en el propio aeropuerto (Farallones) o llevan el carro hasta allá\n"
          "sin costo si el alquiler es de 3 días o más (WayCarCali).\n\n"
          "Se aterriza, se recoge el carro ahí mismo y se devuelve en el aeropuerto antes de volar.\n"
          "Ir a la ciudad a buscarlo solo sumaría un taxi y tiempo, sin ahorrar nada.\n\n"
          "El carro se cobra por días de 24 h; conservarlo hasta el vuelo de la noche suma un cuarto día,\n"
          "pero cubre el tramo entre dejar el hostal y volar, con las maletas encima."), 18, C_INK)

    # 7 movilidad — cuánto carro
    s = prs.slides.add_slide(blank); fondo(s, C_WHITE); barra_titulo(s, "Cuánto carro llevar")
    cd = CategoryChartData()
    nombres_cortos = ["Carro todo el viaje", "Carro solo 3 días", "Sin carro propio"]
    cd.categories = nombres_cortos
    cd.add_series("Por persona (COP)", [m["pp"] for m in MOVILIDAD])
    gx = s.shapes.add_chart(XL_CHART_TYPE.BAR_CLUSTERED, Inches(0.7), Inches(1.4), Inches(8.2), Inches(5.4), cd).chart
    gx.has_legend = False
    ser = gx.plots[0].series[0]
    for idx, m in enumerate(MOVILIDAD):
        pt = ser.points[idx]; pt.format.fill.solid()
        pt.format.fill.fore_color.rgb = C_ACC if m["recomendado"] else RGBColor.from_string("D8C4B2")
    caja(s, Inches(9.1), Inches(1.8), Inches(3.9), Inches(4.6),
         (f"★ Recomendado: carro propio todo el viaje, {cop(MOV_RECO['pp'])} por persona.\n\n"
          f"Ahorro máximo sin carro propio: {cop(125_000)}.\n\n"
          "El mostrador de las marcas grandes costaría casi el doble: no hace falta."), 16, C_PRIM_D)

    # 8 recomendación
    s = prs.slides.add_slide(blank); fondo(s, C_PRIM)
    caja(s, Inches(0.8), Inches(0.6), Inches(11.7), Inches(0.9), "La recomendación", 32, C_WHITE, True)
    banda = s.shapes.add_shape(1, Inches(0.8), Inches(1.8), Inches(11.7), Inches(1.25))
    banda.fill.solid(); banda.fill.fore_color.rgb = C_ACC; banda.line.fill.background()
    tf = banda.text_frame; tf.word_wrap = True; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    pr = tf.paragraphs[0]; pr.alignment = PP_ALIGN.CENTER
    rr = pr.add_run()
    rr.text = f"{RECO['estadia']}  +  carro propio todo el viaje  ≈  {cop(RECO['total_pp'])} por persona"
    rr.font.size = Pt(20); rr.font.bold = True; rr.font.color.rgb = C_INK
    caja(s, Inches(0.9), Inches(3.4), Inches(11.5), Inches(3.4),
         ("Hostal que dice sí a todo (seguridad, piscina, aire, bar, rumba y salsa para conocer gente) y una\n"
          "movilidad sin vueltas a la ciudad ni hueco final con maletas.\n\n"
          f"• Ahorro: moverse sin carro propio = {cop(_pp_estadia(MEJOR) + 125_000)} — entra en meta.\n"
          f"• No pasar de 400 mil en estadía: Patio del Río = {cop(PAQUETES[1]['total_pp'])} (piscina + aire)."),
         18, C_WHITE)

    # 9 antes de reservar + links
    s = prs.slides.add_slide(blank); fondo(s, C_WHITE); barra_titulo(s, "Antes de reservar")
    caja(s, Inches(0.9), Inches(1.5), Inches(11.5), Inches(3.0),
         ("1. Estadía: confirmar si el precio es por persona o por habitación, y capacidad para 7 (camas ≥5).\n"
          "2. Carro: llamar por WhatsApp a Farallones o WayCarCali para cerrar la van de 7 puestos y la entrega\n"
          "     en el aeropuerto.\n"
          "3. Confirmar el precio del cuarto día para conservar el carro hasta el vuelo de la noche.\n"
          "4. Reservar pronto: cinco semanas y fin de semana de Halloween."), 18, C_INK)
    tb = s.shapes.add_textbox(Inches(0.9), Inches(5.0), Inches(11.5), Inches(1.6)); tf = tb.text_frame; tf.word_wrap = True
    p0 = tf.paragraphs[0]; run = p0.add_run(); run.text = "Estadía:  "
    run.font.size = Pt(13); run.font.color.rgb = C_MUTE
    for e in ESTADIA_RANK:
        run = p0.add_run(); run.text = e["nombre"].split(" (")[0] + "   "
        run.font.size = Pt(13); run.font.color.rgb = C_PRIM_D; run.hyperlink.address = e["url"]
    p1 = tf.add_paragraph(); run = p1.add_run(); run.text = "Carro:  "
    run.font.size = Pt(13); run.font.color.rgb = C_MUTE
    for nombre, url in [("Farallones", FARALLONES_URL), ("WayCarCali", WAYCAR_URL), ("Kayak", KAYAK_URL)]:
        run = p1.add_run(); run.text = nombre + "   "
        run.font.size = Pt(13); run.font.color.rgb = C_PRIM_D; run.hyperlink.address = url
    caja(s, Inches(0.9), Inches(6.6), Inches(11.5), Inches(0.5),
         f"Documentos hermanos: {ARCHIVOS_REF}", 12, C_MUTE)

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
    print("\n✔ 4/4 entregables regenerados (v5: índice + metodología + movilidad en lenguaje llano, sin siglas)")


if __name__ == "__main__":
    main()
