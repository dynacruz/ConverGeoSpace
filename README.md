# 🌍 Un Conversor Geoespacial Web: KML/KMZ ↔ SHP/DXF

Una aplicación web robusta orientada a profesionales de Sistemas de Información Geográfica (SIG) y topografía. Permite la conversión bidireccional entre formatos geoespaciales ampliamente utilizados, garantizando precisión espacial y conservación de atributos.

## ✨ Características Principales

* **Conversión Multiformato:**
  - KML / KMZ → SHP (Shapefile)
  - KML / KMZ → DXF (CAD)
  - SHP → KMZ (Google Earth)

* **Extracción Automática:**  
  Soporte nativo para archivos `.kml` y `.kmz`, incluyendo descompresión automática.

* **Reproyección Espacial Precisa:**  
  Transformación de coordenadas geográficas (EPSG:4326) a sistemas UTM (zonas 17S, 18S, 17N, 18N) mediante `pyproj`.

* **Integridad de Atributos:**  
  Conservación completa de la tabla de atributos.  
  Incluye truncamiento inteligente de nombres de campos (≤10 caracteres) para compatibilidad con `.dbf`.

* **Salida Profesional Dual:**  
  - Shapefiles (`.shp`, `.shx`, `.dbf`, `.prj`) compatibles con QGIS/ArcGIS  
  - Archivos `.dxf` listos para flujos CAD

* **Exportación a Google Earth:**  
  Conversión de SHP a KMZ optimizada para visualización en entornos web y escritorio.

* **Integración CAD / AutoLISP:**  
  Incluye rutina `ImportarTopografia.lsp` para inserción automatizada en AutoCAD Civil 3D.

---

## 🛠️ Casos de Uso

Ideal para:

- Procesamiento de levantamientos topográficos  
- Estandarización de datos espaciales  
- Preparación de insumos para tasación predial  
- Integración SIG ↔ CAD  
- Automatización de flujos geoespaciales  

---

## 💻 Tecnologías Utilizadas

* **Backend:** Python 3.12, FastAPI, Uvicorn  
* **Motor Geoespacial:** GeoPandas, Fiona, PyProj, Shapely (basados en GDAL/OGR)  
* **Frontend:** HTML5, JavaScript, Tailwind CSS  
* **Integración CAD:** AutoLISP  

---

## 🚀 Instalación y Despliegue Local

Debido a que el motor geoespacial depende de binarios nativos (GDAL), se recomienda el uso de Conda (Miniconda/Anaconda) en entornos Windows.

### 1. Clonar el repositorio y preparar el entorno

```bash
git clone https://github.com/TU_USUARIO/ConverGeoSpace.git
cd ConverGeoSpace

conda create -n geo_env python=3.12 -y
conda activate geo_env