# geoia-bloom-huasco

**Dinámica espacio-temporal del bloom (Desierto Florido) en la cuenca del río Huasco, Chile — Análisis con NDVI MODIS**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Google Earth Engine](https://img.shields.io/badge/Google%20Earth%20Engine-4285F4?logo=google&logoColor=white)](https://earthengine.google.com/)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/djwillichile/geoia-bloom-huasco/blob/main/notebooks/dinamica_bloom_huasco_ndvi.ipynb)
[![Web](https://img.shields.io/badge/Web-GitHub%20Pages-222?logo=github)](https://djwillichile.github.io/geoia-bloom-huasco/)

**Sitio web del proyecto:** https://djwillichile.github.io/geoia-bloom-huasco/

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
├── CITATION.cff                             # Metadatos de citación
├── LICENSE
├── .gitignore
├── requirements.txt                         # Dependencias pip
├── environment.yml                          # Entorno conda reproducible
├── index.html                               # Sitio web del proyecto (GitHub Pages)
├── .github/
│   └── workflows/
│       └── pages.yml                        # Despliegue automático GitHub Pages
├── notebooks/
│   ├── dinamica_bloom_huasco_ndvi.ipynb     # Análisis principal de bloom
│   └── cartografia_huasco_layout.ipynb      # Layout cartográfico profesional
├── data/                                    # Datos exportados (CSV, GeoJSON)
├── figures/                                 # Figuras y mapas exportados
└── docs/
    ├── metodologia.md                       # Metodología detallada
    └── references.bib                       # Bibliografía en formato BibTeX
```

## Notebooks

### 1. `dinamica_bloom_huasco_ndvi.ipynb`

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/djwillichile/geoia-bloom-huasco/blob/main/notebooks/dinamica_bloom_huasco_ndvi.ipynb)

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

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/djwillichile/geoia-bloom-huasco/blob/main/notebooks/cartografia_huasco_layout.ipynb)

Notebook de cartografía profesional con layout tipo publicación:

- Descarga de capas raster desde GEE (DEM SRTM, NDVI medio MODIS)
- Generación de hillshade y composición visual
- Layout de dos paneles: elevación (izquierda) y NDVI medio (derecha)
- Elementos cartográficos: rosa de los vientos, escala, leyendas
- Exportación a PNG a 300 DPI

## Requisitos

### Entorno conda (recomendado)

```bash
conda env create -f environment.yml
conda activate geoia-bloom-huasco
```

### Entorno pip

```bash
pip install -r requirements.txt
```

### Requisito adicional

- Python 3.10+
- Cuenta de Google Earth Engine autenticada ([registro gratuito](https://earthengine.google.com/))

## Uso rápido

1. Clonar el repositorio:

```bash
git clone https://github.com/djwillichile/geoia-bloom-huasco.git
cd geoia-bloom-huasco
```

2. Crear entorno y activarlo:

```bash
conda env create -f environment.yml
conda activate geoia-bloom-huasco
```

3. Autenticarse en Earth Engine:

```python
import ee
ee.Authenticate()
ee.Initialize(project='tu-proyecto-gee')
```

4. Abrir los notebooks en Jupyter o Google Colab:

| Notebook | Colab |
|---|---|
| Dinámica Bloom NDVI | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/djwillichile/geoia-bloom-huasco/blob/main/notebooks/dinamica_bloom_huasco_ndvi.ipynb) |
| Cartografía Huasco | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/djwillichile/geoia-bloom-huasco/blob/main/notebooks/cartografia_huasco_layout.ipynb) |

## Contexto: Desierto Florido

El **Desierto Florido** es un fenómeno climático-ecológico que ocurre de forma esporádica en el desierto de Atacama, Chile. Se produce cuando precipitaciones inusuales activan el banco de semillas latente, generando una explosión de vegetación efímera que transforma el paisaje árido en extensas praderas floridas.

Este proyecto utiliza el NDVI como proxy para detectar y cuantificar estos eventos de floración a escala de cuenca hidrográfica, proporcionando una perspectiva temporal de más de dos décadas (2000–2026). Los resultados contribuyen al conocimiento de la respuesta de los ecosistemas áridos frente a la variabilidad climática, con implicaciones para la conservación de la biodiversidad del desierto de Atacama.

## Cómo citar

Si utilizas este repositorio en una publicación científica, cita usando la información del archivo [`CITATION.cff`](CITATION.cff):

```
Fuentes Jaque, G. (2025). geoia-bloom-huasco: Dinámica espacio-temporal
del Desierto Florido en la cuenca del río Huasco (NDVI MODIS 2000–2026).
GitHub. https://github.com/djwillichile/geoia-bloom-huasco
```

## Referencias clave

- Didan, K. (2021). MODIS/Terra Vegetation Indices 16-Day L3 Global 250m SIN Grid V061. NASA EOSDIS Land Processes DAAC. https://doi.org/10.5067/MODIS/MOD13Q1.061
- Gorelick, N. et al. (2017). Google Earth Engine: Planetary-scale geospatial analysis for everyone. *Remote Sensing of Environment*, 202, 18–27. https://doi.org/10.1016/j.rse.2017.06.031
- Vidiella, P.E., Armesto, J.J., & Gutiérrez, J.R. (1999). Vegetation changes and sequential flowering after rain in the southern Atacama Desert. *Journal of Arid Environments*, 43(4), 449–458. https://doi.org/10.1006/jare.1999.0563
- Garreaud, R.D. & Rutllant, J. (2003). Factores climatológicos relevantes para el florecimiento del desierto en el norte de Chile. *Revista Chilena de Historia Natural*, 76, 611–628.
- Farr, T.G. et al. (2007). The Shuttle Radar Topography Mission. *Reviews of Geophysics*, 45(2). https://doi.org/10.1029/2005RG000183

> La bibliografía completa en formato BibTeX se encuentra en [`docs/references.bib`](docs/references.bib).

## Licencia

Este proyecto está licenciado bajo la [MIT License](LICENSE).

## Autor

**Guillermo Fuentes Jaque**  
Científico de datos geoespaciales · Consultor ambiental · Docente universitario  
[GitHub: @djwillichile](https://github.com/djwillichile)

---

> Proyecto desarrollado con Google Earth Engine, datos abiertos MODIS/NASA y herramientas de código abierto de Python.
