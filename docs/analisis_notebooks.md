# Análisis técnico de los notebooks

**Fecha de revisión:** 2025-04-29  
**Notebooks evaluados:**
- `notebooks/dinamica_bloom_huasco_ndvi.ipynb` (62 celdas, ~1.4 MB)
- `notebooks/cartografia_huasco_layout.ipynb` (16 celdas, ~2.2 MB)

---

## Resumen ejecutivo

| Aspecto | `dinamica_bloom_huasco_ndvi` | `cartografia_huasco_layout` |
|---|---|---|
| Celdas | 62 | 16 |
| Complejidad | Alta | Media |
| Documentación | Buena | Excelente |
| Reproducibilidad | Media | Alta |
| Manejo de errores | Parcial | Parcial |
| Exportación | CSV + PNG (interactivo) | PNG comentada |
| Modularidad | Media | Alta |

---

## 1. `dinamica_bloom_huasco_ndvi.ipynb`

### Estructura

El notebook se organiza en flujos temáticos bien delimitados por celdas markdown:

| Celdas | Sección |
|---|---|
| 0–2 | Título, instrucciones, instalación de dependencias |
| 3–7 | Definición del AOI, parámetros generales, funciones auxiliares |
| 8–10 | Carga MOD13Q1, climatología por slot16 |
| 11–14 | Anomalía de NDVI, clasificación bloom |
| 15–20 | Métricas de serie temporal, exportación CSV (con widgets) |
| 21–28 | Suavizado Savitzky-Golay, detección de picos, delimitación de eventos |
| 29–32 | Tabla resumen de eventos, interpretación |
| 33–42 | Frecuencia espacial del bloom (mapeo) |
| 43–61 | Visualización alternativa, composites NDVI-max, análisis con ventanas |

### Fortalezas

- Instalación de dependencias en la primera celda ejecutable.
- Proyecto GEE se lee desde Colab Secrets (`userdata.get('projectGEE')`), no hardcodeado.
- Funciones bien nombradas: `add_slot16()`, `preprocess()`, `clim_image_for_slot()`.
- Validaciones con `assert` antes de secciones críticas (celdas 22, 29, 34, 40).
- Constantes clave en mayúsculas: `SCALE_TS`, `SG_WINDOW`, `MIN_DURATION`.
- Try/except en la inicialización de Earth Engine.

### Problemas identificados

#### Crítico — celda 42: `raise KeyboardInterrupt`
```python
raise KeyboardInterrupt("Ejecución detenida por el usuario.")
```
Esta instrucción detiene la ejecución automática del notebook (Run All). Separa dos flujos alternativos de análisis pero rompe la reproducibilidad. Debería eliminarse o reemplazarse por una variable de control:
```python
STOP_BEFORE_ALTERNATIVE = True
if STOP_BEFORE_ALTERNATIVE:
    raise SystemExit("Flujo alternativo omitido.")
```

#### Parámetros sin justificación documentada

| Parámetro | Celda | Valor | Problema |
|---|---|---|---|
| `SG_WINDOW` | 23 | `11` | ¿Por qué 11 y no 9 o 13? No hay nota sobre el criterio |
| `SG_POLY` | 23 | `3` | Sin justificación |
| `PROMINENCE` | 24 | `np.nanpercentile(y_smooth, 90) * 0.5` | ¿Por qué percentil 90 y factor 0.5? |
| `EVENT_RELATIVE_THRESHOLD` | 25 | `0.45` | Sin documentar el criterio del 45% |
| `MERGE_GAP` | 26 | `1` | Equivale a 16 días; no está explicado |
| `MIN_DISTANCE` | 24 | `12` | Equivale a ~192 días; sin comentario |

#### Requests sin timeout
```python
# Celdas 35–42: descarga de thumbnails sin timeout
thumb_url = shaded.getThumbURL(...)
img_data = requests.get(thumb_url).content   # Sin timeout → puede colgarse
```
Recomendación:
```python
img_data = requests.get(thumb_url, timeout=60).content
```

#### Validación de Savitzky-Golay
Si la serie temporal tiene menos puntos que `SG_WINDOW`, `savgol_filter` falla con un error poco descriptivo. Añadir:
```python
assert len(y) >= SG_WINDOW, f"Serie demasiado corta ({len(y)}) para SG_WINDOW={SG_WINDOW}"
```

#### Código duplicado en visualizaciones
El patrón de graficar series temporales con anotaciones de eventos se repite con variaciones menores en celdas 28, 44 y 48. Podría consolidarse en una función `plot_bloom_series(df, events, ...)`.

#### Inconsistencia de fechas con el otro notebook
`START_DATE = '2000-01-01'`, `END_DATE = '2026-12-31'` en este notebook, pero `cartografia_huasco_layout.ipynb` usa `YEAR_START=2002`, `YEAR_END=2023`. Los períodos no coinciden, lo que puede dar lugar a resultados difíciles de comparar.

---

## 2. `cartografia_huasco_layout.ipynb`

### Estructura

Notebook lineal y bien estructurado:

| Celdas | Sección |
|---|---|
| 0–3 | Título, instalación, instrucciones Colab Secrets |
| 4–5 | Imports e inicialización EE |
| 6 | Carga de geometrías (cuenca, regiones, ríos) |
| 8 | DEM SRTM + hillshade + NDVI climatológico en GEE |
| 10 | Descarga de arrays vía `getThumbURL` |
| 12–13 | Función `add_wind_rose()` + layout cartográfico completo |
| 14–15 | Exportación PNG (comentada) |

### Fortalezas

- Notebook más corto y lineal: muy fácil de seguir y reproducir.
- Comentarios muy detallados en todas las celdas.
- Función `add_wind_rose()` bien encapsulada y reutilizable.
- Variables de control bien nombradas: `EXT_MAIN`, `EXT_REG`, `EXT_CHL`.
- Cartografía completa: rosa de vientos, barra de escala, leyenda, créditos, graticulas.
- Exportación a 300 DPI lista (solo necesita descomentarse).

### Problemas identificados

#### Celda 13 de 284 líneas
Todo el layout cartográfico está en una sola celda. Si falla en la línea 200, hay que relanzar las 284 líneas. Recomendación: dividir en al menos 3 celdas temáticas:
1. Configuración de la figura y subplots
2. Panel izquierdo (DEM/hillshade)
3. Panel derecho (NDVI) + elementos cartográficos

#### Dimensiones de thumbnail inconsistentes
```python
thumb_dem  = shaded.getThumbURL({'dimensions': 1200, ...})
thumb_ndvi = ndvi_shaded.getThumbURL({'dimensions': 800, ...})
```
Las dimensiones distintas pueden causar desalineación de las grillas al superponer capas. Deberían usar la misma resolución o justificarse explícitamente.

#### Umbral de transparencia hardcodeado
```python
es_blanco = (ndvi_2d[:,:,0] > 240) & (ndvi_2d[:,:,1] > 240) & (ndvi_2d[:,:,2] > 240)
```
El valor `240` no está documentado. Un comentario explicando que corresponde al fondo blanco del thumbnail de GEE mejoraría la legibilidad.

#### Coordenadas del outlet sin comentario
```python
outlet = ee.Geometry.Point([-71.17, -28.47])
```
No queda claro que es la desembocadura del río Huasco. Debería tener un comentario.

#### Exportación comentada
La celda de exportación final está comentada, lo que obliga a ejecutarla manualmente. Podría controlarse con una variable:
```python
EXPORT_PNG = True  # Cambiar a False para omitir
if EXPORT_PNG:
    fig.savefig('/content/cartografia_huasco.png', dpi=300, bbox_inches='tight')
```

#### `warnings.filterwarnings('ignore')`
Deshabilita todas las advertencias, incluyendo las de Cartopy y GeoPandas sobre CRS. Puede ocultar problemas reales. Mejor usar filtros específicos:
```python
import warnings
warnings.filterwarnings('ignore', category=UserWarning, module='cartopy')
```

---

## Recomendaciones prioritarias

### Para ambos notebooks

1. **Sincronizar fechas**: Usar el mismo rango temporal (`2000–2026`) en ambos notebooks o documentar explícitamente por qué difieren.
2. **Agregar `timeout` a `requests.get()`**: Evita que el notebook se cuelgue indefinidamente en descargas de GEE.
3. **Archivo de configuración**: Un `config.py` o celda de parámetros al inicio con todos los umbrales y constantes facilita la experimentación y la reproducibilidad.

### Para `dinamica_bloom_huasco_ndvi.ipynb`

4. **Eliminar o condicionalizar** la celda con `raise KeyboardInterrupt` (celda 42).
5. **Documentar criterios** de los parámetros de detección de eventos (`SG_WINDOW`, `PROMINENCE`, `EVENT_RELATIVE_THRESHOLD`), aunque sea con una nota breve.
6. **Validar longitud de serie** antes de `savgol_filter`.
7. **Consolidar funciones de visualización** duplicadas.

### Para `cartografia_huasco_layout.ipynb`

8. **Dividir celda 13** en 3–4 celdas temáticas.
9. **Unificar dimensiones de thumbnail** o documentar la diferencia.
10. **Descommentar exportación** con variable de control `EXPORT_PNG`.
