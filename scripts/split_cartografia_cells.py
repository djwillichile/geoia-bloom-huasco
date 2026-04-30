#!/usr/bin/env python3
"""
Reorganiza cartografia_huasco_layout.ipynb:
  1. Divide celda 5 en: (a) imports + warnings, (b) inicialización EE
  2. Mueve la import faltante (shapely.box) a la celda de imports
  3. Elimina imports duplicados al inicio de la celda 12
  4. Divide la celda 12 en 4 celdas temáticas
"""
import json, copy
from pathlib import Path


def make_code_cell(source: str) -> dict:
    lines = source.rstrip("\n").split("\n")
    src_list = [line + "\n" for line in lines]
    src_list[-1] = src_list[-1].rstrip("\n")
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": src_list,
    }


def make_markdown_cell(source: str) -> dict:
    lines = source.rstrip("\n").split("\n")
    src_list = [line + "\n" for line in lines]
    src_list[-1] = src_list[-1].rstrip("\n")
    return {"cell_type": "markdown", "metadata": {}, "source": src_list}


path = Path("notebooks/cartografia_huasco_layout.ipynb")
with open(path, encoding="utf-8") as f:
    nb = json.load(f)

cells = nb["cells"]

# ══════════════════════════════════════════════════════════════════════════════
# 1. Dividir celda 5 en imports y EE init
# ══════════════════════════════════════════════════════════════════════════════
IMPORTS_CELL = """\
import ee, geemap, numpy as np, warnings, requests
import geopandas as gpd
from shapely.geometry import shape
from shapely.geometry import box as shapely_box
from PIL import Image
from io import BytesIO
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.colors as mcolors
import matplotlib.gridspec as gridspec
import matplotlib.patheffects as pe
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.cm import ScalarMappable
from matplotlib_scalebar.scalebar import ScaleBar
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
from google.colab import userdata

# Silenciar advertencias de proyecciones de Cartopy y GeoPandas
warnings.filterwarnings('ignore', category=UserWarning, module='cartopy')
warnings.filterwarnings('ignore', category=UserWarning, module='geopandas')
warnings.filterwarnings('ignore', message='.*CRS.*')"""

EE_INIT_CELL = """\
# ── Leer proyecto desde Secrets ───────────────────────────────────────────────
try:
    PROJECT_ID = userdata.get('projectGEE')
except Exception:
    PROJECT_ID = None

# Si no está en Secrets, pedir manualmente
if not PROJECT_ID:
    print('⚠️  No se encontró el Secret "projectGEE".')
    print('   Opciones:')
    print('   1) Agrega tu proyecto en el panel 🔑 (Secrets) con clave: projectGEE')
    print('   2) O ingrésalo manualmente a continuación:\\n')
    PROJECT_ID = input('   Ingresa tu Google Cloud Project ID: ').strip()

# ── Inicializar Earth Engine ──────────────────────────────────────────────────
try:
    ee.Initialize(project=PROJECT_ID)
    print('✅ Earth Engine inicializado correctamente.')
except Exception:
    print('Autenticando...')
    ee.Authenticate()
    ee.Initialize(project=PROJECT_ID)
    print('✅ Earth Engine inicializado tras autenticación.')"""

# Reemplazar celda 5 con la de imports y agregar nueva celda de EE init
cells[5] = make_code_cell(IMPORTS_CELL)
cells.insert(6, make_code_cell(EE_INIT_CELL))
print("  ✓ Celda 5 dividida: imports | EE init (nueva celda 6)")

# ══════════════════════════════════════════════════════════════════════════════
# 2. Dividir la celda 12 (ahora índice 13 tras insertar 1)
# ══════════════════════════════════════════════════════════════════════════════
IDX = 13  # índice actualizado tras la inserción

src_12 = "".join(cells[IDX]["source"])
lines_12 = src_12.split("\n")

# Los primeros 6 líneas son imports duplicados + la línea vacía 7
# Líneas a partir del 8 (índice 7) empiezan con CRS = ...
# Encontrar el inicio real del código (tras los imports duplicados)
start = 0
for i, ln in enumerate(lines_12):
    if ln.startswith("CRS"):
        start = i
        break

code_body = "\n".join(lines_12[start:])
body_lines = code_body.split("\n")

# ── Localizar separadores por comentarios de sección ──────────────────────────
def find_line(lines, pattern, start=0):
    for i, ln in enumerate(lines[start:], start):
        if pattern in ln:
            return i
    return None

# Sección A: CRS/BG/EXT/rivers/colormaps → hasta def add_scalebar
idx_scalebar = find_line(body_lines, "def add_scalebar(")
# Sección B: add_scalebar + label_river → hasta fig = plt.figure
idx_fig = find_line(body_lines, "fig = plt.figure(")
# Sección C: fig + paneles izquierdo + leyenda → hasta PANEL PRINCIPAL
idx_main = find_line(body_lines, "# PANEL PRINCIPAL")
# Sección D: panel principal + título + show → hasta el final

part_A = "\n".join(body_lines[:idx_scalebar]).rstrip()
part_B = "\n".join(body_lines[idx_scalebar:idx_fig]).rstrip()
part_C = "\n".join(body_lines[idx_fig:idx_main]).rstrip()
part_D = "\n".join(body_lines[idx_main:]).rstrip()

# Encabezados descriptivos para cada sección
HEADER_A = """\
# ── Constantes, paletas de color y mappables ──────────────────────────────────"""

HEADER_B = """\
# ── Funciones auxiliares de cartografía ───────────────────────────────────────"""

HEADER_C = """\
# ── Figura: configuración y panel izquierdo (regional + leyenda) ──────────────"""

HEADER_D = """\
# ── Panel principal (DEM / NDVI) + título y créditos ─────────────────────────"""

cell_A = make_code_cell(HEADER_A + "\n" + part_A)
cell_B = make_code_cell(HEADER_B + "\n" + part_B)
cell_C = make_code_cell(HEADER_C + "\n" + part_C)
cell_D = make_code_cell(HEADER_D + "\n" + part_D)

# Reemplazar la celda grande por las 4 nuevas
cells[IDX:IDX+1] = [cell_A, cell_B, cell_C, cell_D]
print("  ✓ Celda 12 dividida en 4 celdas (A: constantes, B: funciones, C: panel izq., D: panel princ.)")

# ══════════════════════════════════════════════════════════════════════════════
# 3. Guardar
# ══════════════════════════════════════════════════════════════════════════════
nb["cells"] = cells
with open(path, "w", encoding="utf-8") as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print(f"\n  Total de celdas: {len(cells)}")
print("  ✅ Notebook guardado.")
