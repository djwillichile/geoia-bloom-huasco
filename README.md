# geoia-bloom-huasco

**Dinámica espacio-temporal del bloom (Desierto Florido) en la cuenca del río Huasco, Chile — Análisis con NDVI MODIS**

---

## Descripción

Este repositorio contiene un flujo de trabajo reproducible para analizar la dinámica de la vegetación efímera asociada al fenómeno del **Desierto Florido** en la cuenca del río Huasco (Región de Atacama, Chile), utilizando series temporales de **NDVI** derivadas del sensor **MODIS** (producto MOD13Q1, Collection 6.1).

El análisis combina **Google Earth Engine (API de Python)**, procesamiento geoespacial y visualización cartográfica para:

1. Construir una **climatología estacional de NDVI** en intervalos de 16 días (slot16).
2. Calcular **anomalías de NDVI** respecto de la climatología como indicador de bloom.
3. Detectar y cuantificar **eventos de floración** en la cuenca del Huasco (2000–2026).
4. Generar **cartografía profesional** del área de estudio (elevación, NDVI medio, cuenca hidrográfica).

## Área de estudio

| Parámetro | Valor |
|---|---|
| **Cuenca** | Río Huasco (HydroBASINS Level 6) |
| **Región** | Atacama, Chile |
| **Coordenadas aprox.** | 28.5°S, 70.5°W |
| **Contexto ecológico** | Desierto de Atacama — zona de Desierto Florido |

## Datos utilizados

| Dataset | Fuente | Resolución | Período |
|---|---|---|---|
| **MOD13Q1** (NDVI 16 días) | MODIS / NASA — GEE | 250 m | 2000–2026 |
| **SRTM** (DEM) | USGS — GEE | 30 m | — |
| **FAO/GAUL** (límites admin.) | FAO — GEE | — | 2015 |
| **HydroBASINS** | WWF/HydroSHEDS — GEE | — | v1 |

## Metodología

### Definición de bloom

Se define un píxel como **bloom** cuando se cumplen simultáneamente dos condiciones:

- `NDVI > 0.20` (umbral de vegetación activa)
- `Anomalía > 0.02` (incremento respecto de la climatología del slot16)

Donde:

```
Anomaly = NDVI_observado − NDVI_climatología(slot16)
Bloom   = (NDVI > 0.20) AND (Anomaly > 0.02)
```

### Flujo de procesamiento

```
MOD13Q1 (2000-2026)
  ├── Preprocesamiento (escala, QA filter: SummaryQA ≤ 1)
  ├── Asignación de slot16 = floor(DOY / 16)
  ├── Climatología: mean(NDVI) por slot16
  ├── Anomalía: NDVI − climatología(slot16)
  ├── Clasificación Bloom
  ├── Métricas temporales:
  │     ├── bloom_area_km2
  │     ├── bloom_ndvi_mean / bloom_ndvi_sd
  │     ├── basin_ndvi_mean / basin_ndvi_sd
  │     └── basin_anom_mean
  ├── Detección de eventos (suavizado Savitzky-Golay + picos)
  └── Cartografía: frecuencia espacial del bloom
```

### Métricas calculadas

| Métrica | Descripción |
|---|---|
| `bloom_area_km2` | Área total con condición de bloom (km²) |
| `bloom_ndvi_mean` | NDVI medio en píxeles bloom |
| `bloom_ndvi_sd` | Desviación estándar del NDVI en píxeles bloom |
| `basin_ndvi_mean` | NDVI medio de toda la cuenca |
| `basin_ndvi_sd` | Desviación estándar del NDVI en la cuenca |
| `basin_anom_mean` | Anomalía media del NDVI en la cuenca |

## Estructura del repositorio

```
geoia-bloom-huasco/
├── README.md
├── LICENSE
├── .gitignore
├── requirements.txt
├── notebooks/
│   ├── dinamica_bloom_huasco_ndvi.ipynb    # Análisis principal de bloom
│   └── cartografia_huasco_layout.ipynb     # Layout cartográfico profesional
├── data/                                    # Datos exportados (CSV, GeoJSON)
│   └── .gitkeep
├── figures/                                 # Figuras y mapas exportados
│   └── .gitkeep
└── docs/                                    # Documentación adicional
    └── metodologia.md
```

## Notebooks

### 1. `dinamica_bloom_huasco_ndvi.ipynb`

Notebook principal que implementa el flujo completo de análisis:

- Inicialización de Google Earth Engine
- Definición del área de estudio (provincia y cuenca del Huasco)
- Carga y preprocesamiento de MOD13Q1
- Construcción de climatología estacional por slot16
- Cálculo de anomalías y clasificación de bloom
- Extracción de métricas temporales (serie 2000–2026)
- Detección de eventos de bloom (Savitzky-Golay, derivadas, picos)
- Frecuencia espacial del bloom en eventos principales
- Visualización de series temporales y composites NDVI

### 2. `cartografia_huasco_layout.ipynb`

Notebook de cartografía profesional con layout tipo publicación:

- Descarga de capas raster desde GEE (DEM SRTM, NDVI medio MODIS)
- Generación de hillshade y composición visual
- Layout de dos paneles: elevación (izquierda) y NDVI medio (derecha)
- Elementos cartográficos: rosa de los vientos, escala, leyendas
- Exportación a PNG a 300 DPI

## Requisitos

### Entorno

- Python 3.8+
- Cuenta de Google Earth Engine autenticada

### Dependencias principales

```
earthengine-api
geemap
matplotlib
numpy
pandas
scipy
geopandas
cartopy
Pillow
```

Para instalar todas las dependencias:

```bash
pip install -r requirements.txt
```

## Uso rápido

1. Clonar el repositorio:

```bash
git clone https://github.com/djwillichile/geoia-bloom-huasco.git
cd geoia-bloom-huasco
```

2. Instalar dependencias:

```bash
pip install -r requirements.txt
```

3. Autenticarse en Earth Engine:

```python
import ee
ee.Authenticate()
ee.Initialize(project='tu-proyecto-gee')
```

4. Abrir los notebooks en Google Colab o Jupyter:

| Notebook | Colab |
|---|---|
| Dinámica Bloom NDVI | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/djwillichile/geoia-bloom-huasco/blob/main/notebooks/dinamica_bloom_huasco_ndvi.ipynb) |
| Cartografía Huasco | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/djwillichile/geoia-bloom-huasco/blob/main/notebooks/cartografia_huasco_layout.ipynb) |

## Contexto: Desierto Florido

El **Desierto Florido** es un fenómeno climático-ecológico que ocurre de forma esporádica en el desierto de Atacama, Chile. Se produce cuando precipitaciones inusuales activan el banco de semillas latente, generando una explosión de vegetación efímera que transforma el paisaje árido en extensas praderas floridas.

Este proyecto utiliza el NDVI como proxy para detectar y cuantificar estos eventos de floración a escala de cuenca hidrográfica, proporcionando una perspectiva temporal de más de dos décadas (2000–2026).

## Licencia

Este proyecto está licenciado bajo la [MIT License](LICENSE).

## Autor

**Guillermo Fuentes Jaque**
Científico de datos geoespaciales · Consultor ambiental · Docente universitario
[GitHub: @djwillichile](https://github.com/djwillichile)

---

> Proyecto desarrollado con Google Earth Engine, datos abiertos MODIS/NASA y herramientas de código abierto.
