# 🌍 ConverGeoSpace: Conversor Geoespacial Web KML/KMZ ↔ SHP/DXF

Una aplicación web robusta orientada a profesionales de Sistemas de Información Geográfica (SIG) y topografía. Permite la conversión bidireccional entre formatos geoespaciales ampliamente utilizados, garantizando precisión espacial, conservación de atributos y enriquecimiento automático de la geometría.

---

## 🚀 ¿Cómo iniciar la aplicación? (Acceso Rápido)

¡Acceder a la aplicación es muy sencillo y directo!
En la carpeta principal del proyecto encontrarás un archivo diseñado específicamente para arrancar todo el sistema con un solo clic.

Solo haz doble clic en el archivo:
🚀 **`1-INICIAR_APLICACION.bat`**

> Una vez ejecutado, espera unos segundos. La aplicación iniciará el servidor local y te indicará la ruta web (por defecto `http://127.0.0.1:8000`) a la que puedes acceder desde tu navegador favorito para empezar a convertir tus archivos.

---

## ✨ Características y Nuevas Funciones

* **Conversión Multiformato Optimizada:**
  - KML / KMZ → SHP (Shapefile)
  - KML / KMZ → DXF (AutoCAD / CAD) mediante la avanzada librería `ezdxf`
  - Paquetes SHP/ZIP → KMZ (Google Earth)

* **📏 Cálculo Geométrico Automático (¡NUEVO!):**  
  Durante la traducción, la aplicación calcula e inyecta propiedades valiosas en tus atributos:
  - **Polígonos:** Área total (m²), Perímetro (m), y Coordenadas del Centroide (X, Y).
  - **Líneas (Rutas):** Longitud o Perímetro (m).
  - **Puntos:** Ubicación en Coordenadas (X, Y).

* **Reproyección Espacial Automatizada:**  
  Transformación de coordenadas geográficas (WGS84 / EPSG:4326) a los sistemas métricos UTM (zonas 17S, 18S, 17N, 18N) a través de `pyproj`.

* **Integridad y Conservación de Atributos:**  
  Extrae de forma limpia todos los campos descriptivos de las tablas de datos (ExtendedData) de los KML/KMZ.
  Truncamiento automático e inteligente de nombres de campo (≤10 caracteres) para total compatibilidad con estándares DBF/Shapefile.

* **Integración CAD / AutoLISP:**  
  Ahora ubicado de forma organizada en la carpeta `cad_tools`, incluye la rutina `ImportarTopografia.lsp` para una inserción fluida de tus resultados en AutoCAD Civil 3D.

---

## 🛠️ Casos de Uso Frecuentes

Ideal para profesionales, ingenieros y especialistas que requieran:

- Simplificar y acelerar procesamientos de levantamientos topográficos.
- Estandarización rápida de datos espaciales.
- Calcular automáticamente áreas, perímetros y coordenadas sin abrir QGIS/ArcGIS.
- Transformar datos rápidos de Google Earth hacia plataformas de ingeniería asistida por computadora (CAD).
- Generación rápida de insumos para tasación predial y catastro.

---

## 📂 Estructura del Proyecto

El proyecto está diseñado para ser limpio y fácil de entender por cualquier usuario u otro desarrollador:

- `/` (Raíz): Contiene `1-INICIAR_APLICACION.bat`, configuraciones principales y los scripts base (`main.py`, `requirements.txt`).
- `static/`: Contiene la maravillosa y fluida interfaz visual (Frontend) en HTML y Tailwind CSS.
- `cad_tools/`: Rutinas y complementos complementarios para usuarios de CAD (LISP o rutinas externas).
- `tests/`: Scripts utilizados para pruebas estructurales y compilación.
- `build_tools/`: Contiene los scripts y el archivo de especificaciones `.spec` necesarios si quieres compilar la app en un ejecutable cerrado (`.exe`) sin necesidad de Anaconda o Python instalado.

---

## 💻 Entorno y Tecnologías Base

* **Backend Servidor:** Python 3.12, FastAPI, Uvicorn
* **Motor Geoespacial Subyacente:** GeoPandas, Fiona, PyProj, Shapely, Ezdxf
* **Frontend y UI:** HTML5 + JavaScript Vainilla, Tailwind CSS (Modo Oscuro Glassmorphism)

> **Nota para Desarrolladores:**
> Debido a dependencias estrictas de binarios como GDAL (vía Fiona y Geopandas), se recomienda fervientemente utilizar entornos de `Conda` (Miniconda o Anaconda) si deseas modificar o correr el código fuente en Windows en lugar de pip nativo. 
> 
> ```bash
> conda create -n geo_env python=3.12
> conda activate geo_env
> pip install -r requirements.txt
> ```