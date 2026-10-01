# 🐍 ClearNote Py DA — Plantilla Dev Container para análisis de datos en Python

Plantilla **reproducible, ligera y portable** para proyectos de análisis de datos en Python sobre
**VS Code + Dev Containers + Docker + `uv`**. El objetivo es trabajar en un entorno **aislado y
consistente**, sin instalar el toolchain del proyecto en tu máquina anfitriona.

> **¿Buscas cómo trabajamos día a día (la dinámica agente ⇄ tú)?** Eso vive en **[`README_AGENTS.md`](./README_AGENTS.md)**.
> Este archivo es el *qué es y cómo se instala*; ese otro es el *cómo colaboramos*.

---

## ✅ Requisitos previos

- **Docker** en ejecución (en Windows, vía **WSL2**).
- **Visual Studio Code** con la extensión **Dev Containers** (`ms-vscode-remote.remote-containers`).
- **Git**.

No necesitas Python ni `uv` instalados en el host: viven dentro del contenedor.

---

## 🚀 Instalación y uso

### 1. Clona el repositorio

**Por HTTPS:**

```bash
git clone https://github.com/ClearNote97/ClearNote_Py_DA.git
cd ClearNote_Py_DA
```

**Por SSH:**

```bash
git clone git@github.com:ClearNote97/ClearNote_Py_DA.git
cd ClearNote_Py_DA
```

### 2. Elimina el historial de la plantilla

Esto es una **plantilla, no un proyecto en sí**: soltar el historial git que trae es **obligatorio**.

```bash
rm -rf .git
```

### 3. Renombra la carpeta

Ponle el nombre de tu proyecto (reemplaza `nuevo_nombre`):

```bash
cd ..
mv ClearNote_Py_DA nuevo_nombre
cd nuevo_nombre
```

### 4. Inicializa tu propio repositorio *(opcional)*

```bash
git init
git add .
git commit -m "Proyecto inicial basado en la plantilla ClearNote Py DA"
```

Y, si quieres conectarlo a un remoto:

```bash
git remote add origin https://github.com/tu_usuario/tu_repositorio.git
git push -u origin main
```

### 5. Abre en el contenedor

En VS Code: **Ctrl+Shift+P → Reopen in Container**. Espera a que termine el `postCreateCommand`
(prepara `.venv` e instala/sincroniza dependencias con `uv`). **No corras `pip install` a mano.**

---

## ⚙️ Especificaciones técnicas

### Contenedor

| | |
|---|---|
| Imagen base | `python:3.14.5-slim-bookworm` |
| Paquetes de sistema | `build-essential`, `ca-certificates` |
| Gestor de dependencias | `uv` `0.11.13` (copiado desde `ghcr.io/astral-sh/uv`) |
| Usuario | `root` |
| Workspace | `/workspaces/<nombre-de-la-carpeta>` |
| Entorno virtual | `.venv/` (intérprete: `${workspaceFolder}/.venv/bin/python`) |

### Gestión de dependencias con `uv`

`uv` reemplaza a `pip` como herramienta de trabajo (más rápido, lockfiles reproducibles). Al crear el
contenedor, el `postCreateCommand` detecta el estado del proyecto y actúa solo:

| Estado del repo | Qué ejecuta |
|---|---|
| Hay `pyproject.toml` **y** `uv.lock` | `uv sync --locked` (entorno idéntico y reproducible) |
| Hay `pyproject.toml` **sin** `uv.lock` | `uv lock && uv sync` |
| Solo `requirements.txt` | `uv init --no-package --no-workspace .` → borra `main.py` → `uv add -r requirements.txt` (genera `pyproject.toml` + `uv.lock`) |
| No hay ninguno | Falla con mensaje de error |

> **Transición `requirements.txt` → `pyproject.toml` + `uv.lock`:** la plantilla nace con
> `requirements.txt` (Estado 0) y en el primer arranque consolida el lockfile reproducible (Estado N).
> **Cuando `uv.lock` se genere o cambie, se versiona** — es la garantía de reproducibilidad.

### Editor (VS Code)

- **Formateo y linting con Ruff**: formateo al guardar + `fixAll` y `organizeImports` en cada guardado.
- **Type checking**: Pylance en modo `basic`, con *inlay hints* de tipos de variables y retornos.
- **Extensiones preinstaladas**: Python, Pylance, Ruff, Jupyter, Even Better TOML, GitHub Copilot,
  Path Intellisense, Material Icon Theme.

---

## 📂 Estructura del proyecto

```
.
├── .devcontainer/      # Dockerfile + devcontainer.json (definición del entorno)
├── data/               # datos del proyecto
│   └── other/          # archivos de datos en formatos no-SQL (.csv, .parquet, .xlsx, …)
├── docs/               # documentación: objetivo, bitácora de decisiones, diccionario de datos
├── notebooks/          # exploración y prototipado (.py / .ipynb)
├── sandbox/            # experimentos desechables — su contenido NO se versiona
├── tests/              # verificación formal (pytest) — el gate
├── output/             # entregable final, ya verificado
├── src/                # código reutilizable
│   └── utils/          # utilidades
├── .env.example        # plantilla de variables de entorno (copiar a .env)
├── requirements.txt    # dependencias (base para pyproject.toml + uv.lock)
├── README.md           # este archivo (qué es y cómo se instala)
└── README_AGENTS.md     # el contrato de trabajo (dinámica agente ⇄ tú)
```

**Flujo de trabajo:** `sandbox/` (tanteo sucio) → `tests/` (gate que verifica) → `output/` (solo lo
comprobado). Cada carpeta tiene su propio `README.md` explicando su rol. La dinámica completa está en
**[`README_AGENTS.md`](./README_AGENTS.md)**.

---

## 🧹 Qué se versiona y qué no

**Se versiona:** `README.md`, `README_AGENTS.md`, `.devcontainer/*`, `requirements.txt` (o
`pyproject.toml`), `uv.lock` cuando exista, `tests/`, `output/`, los `README.md` de cada carpeta.

**No se versiona:** `.venv/`, `__pycache__/`, `*.pyc`, `.env`, y el **contenido** de `sandbox/`.

`.gitignore` de la plantilla:

```gitignore
.env
__pycache__/
*.pyc
.venv/

# sandbox/: la carpeta y su README viajan; el contenido (experimentos) no se versiona
sandbox/*
!sandbox/README.md
```

> El `.env` **nunca** se versiona. Usa `.env.example` como referencia y crea tu `.env` local.

---

## 📦 Dependencias incluidas

- **Análisis de datos:** `pandas`, `numpy`, `pyarrow`
- **Excel:** `openpyxl`, `xlsxwriter`, `xlrd`, `fastexcel`
- **Notebooks / interactivo:** `ipython`, `ipykernel`, `ipynbname`
- **Utilidades:** `python-dateutil`, `python-dotenv`

---

## ⚖️ Licencia

Distribuido bajo licencia [MIT](https://opensource.org/license/MIT). Puedes copiar, modificar y reutilizar libremente esta plantilla.

## ✍️ Autor

**MSc. Nicolás Enrique Valencia Santiago**

## 🙏 Agradecimientos

Plantilla enriquecida con la asistencia de [Helix — agente de IA](https://github.com/ftuga/helix_asisten) de [ftuga](https://github.com/ftuga).
