#!/usr/bin/env python3
"""
Aplica las correcciones identificadas en el análisis técnico a ambos notebooks.
Ejecutar desde la raíz del repositorio.
"""
import json
from pathlib import Path


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save(nb, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(nb, f, ensure_ascii=False, indent=1)
    print(f"  Guardado: {path}")


def src(cell):
    return "".join(cell["source"])


def set_src(cell, text):
    cell["source"] = [line + "\n" for line in text.rstrip("\n").split("\n")]
    cell["source"][-1] = cell["source"][-1].rstrip("\n")


# ══════════════════════════════════════════════════════════════════════════════
# Notebook 1: dinamica_bloom_huasco_ndvi.ipynb
# ══════════════════════════════════════════════════════════════════════════════
def fix_nb1():
    path = Path("notebooks/dinamica_bloom_huasco_ndvi.ipynb")
    nb = load(path)
    cells = nb["cells"]

    # ── Celda 6 (markdown): actualizar texto de fechas ────────────────────────
    s = src(cells[6])
    s = s.replace("'2014-01-01'", "'2015-01-01'")
    s = s.replace("'2020-03-01'", "'2019-12-31'")
    set_src(cells[6], s)
    print("  nb1 celda 6: fechas del markdown actualizadas")

    # ── Celda 7: rango temporal ───────────────────────────────────────────────
    s = src(cells[7])
    s = s.replace("START_DATE = '2000-01-01'", "START_DATE = '2015-01-01'")
    s = s.replace("END_DATE   = '2026-12-31'", "END_DATE   = '2019-12-31'")
    set_src(cells[7], s)
    print("  nb1 celda 7: START_DATE/END_DATE → 2015-01-01 / 2019-12-31")

    # ── Celda 23: Savitzky-Golay con validación y comentarios ─────────────────
    nuevo_23 = """\
# =====================================================
# Suavizado de la serie temporal
# =====================================================

# SG_WINDOW: número de puntos (impar). 11 puntos × 16 días ≈ 176 días;
#   suficiente para suavizar ruido sin eliminar eventos estacionales.
# SG_POLY: orden del polinomio. 3 preserva bien los picos sin sobre-ajustar.
SG_WINDOW = 11   # debe ser impar
SG_POLY = 3

assert len(y) >= SG_WINDOW, (
    f"Serie demasiado corta ({len(y)} puntos) para SG_WINDOW={SG_WINDOW}. "
    "Reduce SG_WINDOW o amplía el rango de fechas."
)

y_smooth = savgol_filter(y, SG_WINDOW, SG_POLY)
df['bloom_area_smooth'] = y_smooth"""
    set_src(cells[23], nuevo_23)
    print("  nb1 celda 23: comentarios SG + validación de longitud")

    # ── Celda 24: comentarios para MIN_DISTANCE y PROMINENCE ─────────────────
    s = src(cells[24])
    s = s.replace(
        "MIN_DISTANCE = 12",
        "MIN_DISTANCE = 12   # mínimo 12 períodos × 16 días ≈ 192 días entre picos"
    )
    s = s.replace(
        "PROMINENCE = np.nanpercentile(y_smooth, 90) * 0.5",
        (
            "# percentil 90 como referencia del nivel de bloom significativo;\n"
            "# factor 0.5 exige que el pico sobresalga al menos la mitad de ese nivel.\n"
            "PROMINENCE = np.nanpercentile(y_smooth, 90) * 0.5"
        )
    )
    s = s.replace(
        "MIN_PEAK_HEIGHT = np.nanpercentile(y_smooth, 80)",
        "MIN_PEAK_HEIGHT = np.nanpercentile(y_smooth, 80)   # percentil 80: descarta picos menores"
    )
    set_src(cells[24], s)
    print("  nb1 celda 24: comentarios MIN_DISTANCE y PROMINENCE")

    # ── Celda 25: comentarios para EVENT_RELATIVE_THRESHOLD y MIN_DURATION ────
    s = src(cells[25])
    s = s.replace(
        "EVENT_RELATIVE_THRESHOLD = 0.45",
        "EVENT_RELATIVE_THRESHOLD = 0.45   # 45% del pico: delimita los flancos del evento"
    )
    s = s.replace(
        "MIN_DURATION = 4",
        "MIN_DURATION = 4   # 4 períodos × 16 días ≈ 64 días mínimo de duración"
    )
    s = s.replace(
        "MIN_EVENT_AREA = np.nanpercentile(y_smooth, 80)",
        "MIN_EVENT_AREA = np.nanpercentile(y_smooth, 80)   # área mínima para considerar evento"
    )
    set_src(cells[25], s)
    print("  nb1 celda 25: comentarios EVENT_RELATIVE_THRESHOLD y MIN_DURATION")

    # ── Celda 26: comentario MERGE_GAP (ya tiene uno; reforzar) ───────────────
    s = src(cells[26])
    s = s.replace(
        "MERGE_GAP = 1   # ~16 días",
        "MERGE_GAP = 1   # 1 período × 16 días: fusiona eventos separados por ≤16 días"
    )
    set_src(cells[26], s)
    print("  nb1 celda 26: comentario MERGE_GAP ampliado")

    # ── Celda 42: reemplazar raise KeyboardInterrupt ───────────────────────────
    s = src(cells[42])
    if "KeyboardInterrupt" in s:
        nuevo_42 = """\
# ── Punto de parada opcional ───────────────────────────────────────────────
# Establece CONTINUE_ANALYSIS = True para ejecutar el flujo alternativo
# de análisis que viene a continuación (composites por evento).
CONTINUE_ANALYSIS = False

if not CONTINUE_ANALYSIS:
    print("ℹ️  Ejecución detenida antes del flujo alternativo.")
    print("   Cambia CONTINUE_ANALYSIS = True para continuar.")
    raise SystemExit(0)"""
        set_src(cells[42], nuevo_42)
        print("  nb1 celda 42: KeyboardInterrupt → CONTINUE_ANALYSIS flag")

    # ── Celda 52: agregar timeout a requests.get ──────────────────────────────
    s = src(cells[52])
    s = s.replace(
        "r = requests.get(url)\n",
        "r = requests.get(url, timeout=60)\n"
    )
    set_src(cells[52], s)
    print("  nb1 celda 52: timeout=60 en requests.get()")

    save(nb, path)


# ══════════════════════════════════════════════════════════════════════════════
# Notebook 2: cartografia_huasco_layout.ipynb
# ══════════════════════════════════════════════════════════════════════════════
def fix_nb2():
    path = Path("notebooks/cartografia_huasco_layout.ipynb")
    nb = load(path)
    cells = nb["cells"]

    # ── Celda 4: warnings específicos ────────────────────────────────────────
    s = src(cells[4])
    s = s.replace(
        "warnings.filterwarnings('ignore')",
        (
            "# Silenciar solo advertencias de proyecciones de Cartopy y GeoPandas\n"
            "warnings.filterwarnings('ignore', category=UserWarning, module='cartopy')\n"
            "warnings.filterwarnings('ignore', category=UserWarning, module='geopandas')\n"
            "warnings.filterwarnings('ignore', message='.*CRS.*')"
        )
    )
    set_src(cells[4], s)
    print("  nb2 celda 4: warnings.filterwarnings → filtros específicos")

    # ── Celda 6: comentario para outlet ──────────────────────────────────────
    s = src(cells[6])
    s = s.replace(
        "outlet       = ee.Geometry.Point([-71.17, -28.47])",
        "outlet       = ee.Geometry.Point([-71.17, -28.47])   # desembocadura del río Huasco (coordenadas verificadas en HydroSHEDS)"
    )
    set_src(cells[6], s)
    print("  nb2 celda 6: comentario outlet")

    # ── Celda 8: YEAR_START / YEAR_END ───────────────────────────────────────
    s = src(cells[8])
    s = s.replace(
        "YEAR_START,  YEAR_END  = 2002, 2023",
        "YEAR_START,  YEAR_END  = 2015, 2019   # sincronizado con notebook de análisis de bloom"
    )
    set_src(cells[8], s)
    print("  nb2 celda 8: YEAR_START/YEAR_END → 2015/2019")

    # ── Celda 10: dimensiones y timeout ──────────────────────────────────────
    s = src(cells[10])
    # Unificar dimensiones del thumbnail NDVI a 1200
    s = s.replace(
        "'dimensions': 800,",
        "'dimensions': 1200,   # misma resolución que DEM para evitar desalineación de grillas"
    )
    # Agregar timeout a ambos requests.get
    s = s.replace(
        "requests.get(thumb_url).content",
        "requests.get(thumb_url, timeout=60).content"
    )
    s = s.replace(
        "requests.get(ndvi_url).content",
        "requests.get(ndvi_url, timeout=60).content"
    )
    # Documentar umbral 240
    s = s.replace(
        "es_blanco = (ndvi_2d[:,:,0] > 240) & (ndvi_2d[:,:,1] > 240) & (ndvi_2d[:,:,2] > 240)",
        (
            "# Umbral 240/255: los thumbnails de GEE usan blanco puro (#FFFFFF)\n"
            "# como fondo fuera del área enmascarada; se convierte en transparencia.\n"
            "es_blanco = (ndvi_2d[:,:,0] > 240) & (ndvi_2d[:,:,1] > 240) & (ndvi_2d[:,:,2] > 240)"
        )
    )
    set_src(cells[10], s)
    print("  nb2 celda 10: dimensiones unificadas a 1200, timeout=60, comentario umbral")

    # ── Celda 15: exportación con flag EXPORT_PNG ─────────────────────────────
    nuevo_15 = """\
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
    print("ℹ️  Exportación omitida. Cambia EXPORT_PNG = True para guardar la figura.")"""
    set_src(cells[15], nuevo_15)
    print("  nb2 celda 15: exportación con variable EXPORT_PNG")

    save(nb, path)


if __name__ == "__main__":
    print("── Notebook 1 ──────────────────────────────────")
    fix_nb1()
    print("\n── Notebook 2 ──────────────────────────────────")
    fix_nb2()
    print("\n✅ Notebooks actualizados.")
