# Metodología — Dinámica del Bloom en la Cuenca del Huasco

## 1. Contexto

El Desierto Florido es un fenómeno ecológico que se manifiesta de forma esporádica en el desierto de Atacama, Chile. Se caracteriza por la activación masiva de vegetación efímera tras eventos de precipitación anómalos, generando un incremento significativo y transitorio del índice de vegetación normalizado (NDVI) en zonas habitualmente áridas.

Este proyecto utiliza el producto **MODIS MOD13Q1** (NDVI compuesto de 16 días, resolución espacial de 250 m) como fuente principal de datos satelitales para detectar y cuantificar estos eventos a escala de cuenca hidrográfica.

## 2. Área de estudio

La cuenca del río Huasco se ubica en la Región de Atacama, Chile (aproximadamente 28.5°S, 70.5°W). La delimitación se realiza mediante la intersección de:

- **FAO/GAUL Level 2**: para identificar la provincia del Huasco.
- **WWF/HydroSHEDS v1 (Level 6)**: para delimitar la cuenca hidrográfica a partir de un punto de desembocadura definido en coordenadas (-71.17, -28.47).

El área de interés (AOI) se define como la envolvente (bounding box) de la unión entre la provincia y la cuenca, mientras que las métricas se calculan estrictamente dentro de la geometría de la cuenca.

## 3. Preprocesamiento de MOD13Q1

### 3.1 Filtro de calidad

Se aplica un filtro basado en la banda `SummaryQA` del producto MOD13Q1, reteniendo únicamente los píxeles con calidad buena o marginal (`SummaryQA ≤ 1`). Los píxeles que no cumplen este criterio son enmascarados.

### 3.2 Escala del NDVI

El NDVI de MOD13Q1 se almacena como entero con factor de escala de 0.0001. Se aplica la conversión correspondiente para obtener valores en el rango [-1, 1].

### 3.3 Asignación de slot16

Cada imagen se clasifica según su posición dentro del año mediante la variable `slot16`, calculada como:

```
slot16 = floor(DOY / 16)
```

Esto genera 23 intervalos temporales por año (0 a 22), cada uno representando un compuesto de 16 días.

## 4. Climatología estacional

Se construye una climatología de referencia calculando la imagen promedio de NDVI para cada `slot16` a lo largo de todo el período de análisis (2000–2026). El resultado es una colección de 23 imágenes climatológicas que representan el comportamiento fenológico intra-anual esperado de la vegetación.

Adicionalmente, se calcula la climatología máxima (`NDVI_clim_max`) como referencia del máximo potencial de verdor en la cuenca.

## 5. Detección de bloom

### 5.1 Anomalía

Para cada imagen compuesta de 16 días, se calcula la anomalía como la diferencia entre el NDVI observado y la climatología correspondiente a su slot16:

```
Anomaly = NDVI_observado − NDVI_climatología(slot16)
```

### 5.2 Clasificación binaria

Un píxel se clasifica como **bloom** cuando se cumplen simultáneamente:

- `NDVI > 0.20` (umbral de vegetación activa, `var_thr`)
- `Anomaly > 0.02` (umbral de anomalía positiva, `anom_thr`)

Estos umbrales fueron definidos para capturar incrementos significativos de vegetación en un contexto de aridez extrema.

## 6. Métricas de serie temporal

Para cada imagen compuesta de 16 días se extraen las siguientes métricas a nivel de cuenca:

| Métrica | Descripción | Unidad |
|---|---|---|
| `bloom_area_km2` | Suma del área de píxeles clasificados como bloom | km² |
| `bloom_ndvi_mean` | NDVI medio en píxeles bloom | adimensional |
| `bloom_ndvi_sd` | Desviación estándar del NDVI en píxeles bloom | adimensional |
| `basin_ndvi_mean` | NDVI medio en toda la cuenca | adimensional |
| `basin_ndvi_sd` | Desviación estándar del NDVI en la cuenca | adimensional |
| `basin_anom_mean` | Anomalía media del NDVI en la cuenca | adimensional |

## 7. Detección de eventos

### 7.1 Suavizado

La serie temporal de `bloom_area_km2` se suaviza mediante un filtro **Savitzky-Golay** (ventana = 11, orden polinomial = 3) para reducir la variabilidad de corto plazo y resaltar patrones estacionales e interanuales.

### 7.2 Identificación de picos

Se aplica la función `find_peaks` de SciPy sobre la serie suavizada para identificar máximos locales que representan eventos de bloom. Se filtran los picos según:

- **Prominencia mínima**: para descartar fluctuaciones menores.
- **Distancia mínima entre picos**: para evitar detecciones redundantes.

### 7.3 Frecuencia espacial

Para los eventos principales detectados, se calcula un mapa de frecuencia espacial del bloom, representando el número de veces que cada píxel fue clasificado como bloom durante los períodos de evento.

## 8. Cartografía

El notebook de cartografía genera un layout profesional de dos paneles:

- **Panel izquierdo**: Modelo Digital de Elevación (SRTM 30 m) con hillshade.
- **Panel derecho**: NDVI medio climatológico (MODIS MOD13Q1).

Ambos paneles incluyen la delimitación de la cuenca del Huasco, límites administrativos de referencia (regiones de Atacama y Coquimbo), y elementos cartográficos estándar (rosa de los vientos, barra de escala, leyendas de color).

## 9. Referencias

- Didan, K. (2021). MODIS/Terra Vegetation Indices 16-Day L3 Global 250m SIN Grid V061. NASA EOSDIS Land Processes DAAC.
- Farr, T.G. et al. (2007). The Shuttle Radar Topography Mission. Reviews of Geophysics, 45(2).
- Gorelick, N. et al. (2017). Google Earth Engine: Planetary-scale geospatial analysis for everyone. Remote Sensing of Environment, 202, 18–27.
- Vidiella, P.E., Armesto, J.J., & Gutiérrez, J.R. (1999). Vegetation changes and sequential flowering after rain in the southern Atacama Desert. Journal of Arid Environments, 43(4), 449–458.
