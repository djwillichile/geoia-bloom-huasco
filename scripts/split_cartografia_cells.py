#!/usr/bin/env python3
"""
Reorganiza cartografia_huasco_layout.ipynb:
  1. Divide celda 5 en: (a) imports + warnings específicos, (b) inicialización EE
  2. Mueve shapely.box a la celda de imports y elimina imports duplicados de celda 12
  3. Divide la celda 12 en 4 celdas temáticas
  4. Agrega variable EXPORT_PNG en la celda de exportación
"""
import json, uuid
from pathlib import Path


def make_code_cell(source: str, cell_id: str = None) -> dict:
    lines = source.rstrip("\n").split("\n")
    src_list = [line + "\n" for line in lines]
    src_list[-1] = src_list[-1].rstrip("\n")
    return {
        "cell_type": "code",
        "execution_count": None,
        "id": cell_id or uuid.uuid4().hex[:8],
        "metadata": {},
        "outputs": [],
        "source": src_list,
    }


def make_markdown_cell(source: str, cell_id: str = None) -> dict:
    lines = source.rstrip("\n").split("\n")
    src_list = [line + "\n" for line in lines]
    src_list[-1] = src_list[-1].rstrip("\n")
    return {
        "cell_type": "markdown",
        "id": cell_id or uuid.uuid4().hex[:8],
        "metadata": {},
        "source": src_list,
    }


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

cells[5] = make_code_cell(IMPORTS_CELL, cell_id="cell-imports")
cells.insert(6, make_code_cell(EE_INIT_CELL, cell_id="cell-ee-init"))
print("  ✓ Celda 5 dividida: imports | EE init (nueva celda 6)")

# ══════════════════════════════════════════════════════════════════════════════
# 2. Dividir la celda 12 (ahora índice 13 tras insertar 1)
# ══════════════════════════════════════════════════════════════════════════════
IDX = 13  # índice actualizado tras la inserción

src_12 = "".join(cells[IDX]["source"])
lines_12 = src_12.split("\n")

# Encontrar el inicio real del código (tras los imports duplicados)
start = next(i for i, ln in enumerate(lines_12) if ln.startswith("CRS"))
body_lines = lines_12[start:]


def find_line(lines, pattern):
    return next(i for i, ln in enumerate(lines) if pattern in ln)


i_scalebar = find_line(body_lines, "def add_scalebar(")
i_fig      = find_line(body_lines, "fig = plt.figure(")
i_main     = find_line(body_lines, "# PANEL PRINCIPAL")

cells[IDX:IDX+1] = [
    make_code_cell(
        "# ── Constantes, paletas de color y mappables ──────────────────────────────────\n"
        + "\n".join(body_lines[:i_scalebar]).rstrip(),
        cell_id="cell-constants",
    ),
    make_code_cell(
        "# ── Funciones auxiliares de cartografía ───────────────────────────────────────\n"
        + "\n".join(body_lines[i_scalebar:i_fig]).rstrip(),
        cell_id="cell-helpers",
    ),
    make_code_cell(
        "# ── Figura: configuración y panel izquierdo (regional + leyenda) ──────────────\n"
        + "\n".join(body_lines[i_fig:i_main]).rstrip(),
        cell_id="cell-panel-left",
    ),
    make_code_cell(
        "# ── Panel principal (DEM / NDVI) + título y créditos ─────────────────────────\n"
        + "\n".join(body_lines[i_main:]).rstrip(),
        cell_id="cell-panel-main",
    ),
]
print("  ✓ Celda 12 dividida en 4 celdas (constantes, funciones, panel izq., panel princ.)")

# ══════════════════════════════════════════════════════════════════════════════
# 3. Celda de exportación con EXPORT_PNG
# ══════════════════════════════════════════════════════════════════════════════
EXPORT_CELL = """\
# ── Exportación a PNG ──────────────────────────────────────────────────────
# Cambia EXPORT_PNG = True para guardar la figura en disco y descargarla.
EXPORT_PNG = False

if EXPORT_PNG:
    OUT = '/content/cartografia_huasco.png'
    fig.savefig(OUT, dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor())
    print(f'✅ Figura guardada en: {OUT}')
    from google.colab import files
    files.download(OUT)
else:
    print('ℹ️  Exportación omitida. Cambia EXPORT_PNG = True para guardar la figura.')"""

cells[18] = make_code_cell(EXPORT_CELL, cell_id="cell-export")
print("  ✓ Celda export con EXPORT_PNG flag")

# ══════════════════════════════════════════════════════════════════════════════
# 4. Asegurar id en celda 0
# ══════════════════════════════════════════════════════════════════════════════
if "id" not in cells[0]:
    cells[0]["id"] = "md-colab-badge"

# ══════════════════════════════════════════════════════════════════════════════
# 5. Guardar
# ══════════════════════════════════════════════════════════════════════════════
nb["cells"] = cells
with open(path, "w", encoding="utf-8") as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print(f"\n  Total de celdas: {len(cells)}")
print("  ✅ Notebook guardado.")
