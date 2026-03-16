# 🌍 Conversor Geoespacial Web: KML/KMZ a SHP y DXF

Una aplicación web robusta y orientada a profesionales de Sistemas de Información Geográfica (SIG) y topografía. Permite convertir levantamientos y geometrías en formato KML o KMZ a formatos estándar de la industria (Shapefile y DXF), reproyectándolos con precisión milimétrica a coordenadas UTM (WGS84) y conservando intacta la información alfanumérica.

## ✨ Características Principales

* **Extracción Automática:** Soporte nativo para archivos `.kml` y carpetas comprimidas `.kmz`.
* **Reproyección Espacial Precisa:** Transformación automática de coordenadas geográficas (EPSG:4326) a zonas UTM específicas (17S, 18S, 17N, 18N) utilizando `pyproj`.
* **Integridad de Atributos:** Conservación de la tabla de atributos del KML original. Incluye truncamiento inteligente de nombres de columnas a 10 caracteres para garantizar la compatibilidad estricta con el formato `.dbf` de ESRI.
* **Formatos de Salida Dual:** Generación simultánea de Shapefiles (`.shp`, `.shx`, `.dbf`, `.prj`) listos para QGIS/ArcGIS, y archivos CAD (`.dxf`) listos para ingeniería.
* **Sinergia CAD / AutoLISP:** Incluye una rutina LISP (`ImportarTopografia.lsp`) para automatizar la inserción topológicamente correcta del DXF generado directamente en AutoCAD Civil 3D.

## 🛠️ Casos de Uso
Ideal para agilizar procesos de levantamiento topográfico, estandarizar datos espaciales para la tasación de predios, y preparar geometrías limpias para flujos de automatización espacial o análisis multicriterio.

## 💻 Tecnologías Utilizadas

* **Backend:** Python 3.12, FastAPI, Uvicorn
* **Motor Geoespacial:** GeoPandas, Fiona, PyProj, Shapely (basados en GDAL/OGR)
* **Frontend:** HTML5, Vanilla JavaScript, Tailwind CSS
* **Integración CAD:** AutoLISP

## 🚀 Instalación y Despliegue Local

Debido a que el motor geoespacial subyacente requiere binarios C++ (GDAL), **se recomienda estrictamente el uso de Conda** (Miniconda/Anaconda) en entornos Windows para evitar errores de compilación.

### 1. Clonar el repositorio y preparar el entorno
```bash
git clone [https://github.com/TU_USUARIO/conversor_geoespacial.git](https://github.com/TU_USUARIO/conversor_geoespacial.git)
cd conversor_geoespacial

# Crear y activar un entorno virtual con Python 3.12
conda create -n geo_env python=3.12 -y
conda activate geo_env
