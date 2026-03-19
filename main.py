import os
import shutil
import tempfile
import zipfile
import ezdxf
from pathlib import Path
from typing import List
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from starlette.staticfiles import StaticFiles

# Note: geospacial libs might fail on some Python 3.14 environments without wheels
try:
    import geopandas as gpd
    import fiona
    fiona.drvsupport.supported_drivers['KML'] = 'rw'
    fiona.drvsupport.supported_drivers['libkml'] = 'rw'
    fiona.drvsupport.supported_drivers['DXF'] = 'rw'
    HAS_GEO = True
except ImportError:
    HAS_GEO = False

app = FastAPI(title="KML/KMZ to SHP & DXF Converter")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

def cleanup_files(*paths):
    for path in paths:
        try:
            if os.path.isdir(path):
                shutil.rmtree(path)
            elif os.path.exists(path):
                os.remove(path)
        except Exception as e:
            print(f"Error cleaning up {path}: {e}")

def exportar_a_dxf(gdf, output_path):
    doc = ezdxf.new('R2010')
    msp = doc.modelspace()

    def add_geom(geom):
        if geom is None: return
        
        # Check if geometry has Z coordinates
        has_z = False
        try:
            if hasattr(geom, 'coords') and len(geom.coords) > 0 and len(geom.coords[0]) == 3:
                has_z = True
            elif hasattr(geom, 'exterior') and len(geom.exterior.coords) > 0 and len(geom.exterior.coords[0]) == 3:
                has_z = True
        except:
            pass
            
        if geom.geom_type == 'Point':
            msp.add_point(geom.coords[0])
            
        elif geom.geom_type in ['LineString', 'LinearRing']:
            if has_z:
                msp.add_polyline3d(list(geom.coords))
            else:
                msp.add_lwpolyline(list(geom.coords))
                
        elif geom.geom_type == 'Polygon':
            if has_z:
                # ezdxf polyline3d does not have a close flag directly in the same way, we add the first point to the end if needed
                coords = list(geom.exterior.coords)
                msp.add_polyline3d(coords)
                for interior in geom.interiors:
                    msp.add_polyline3d(list(interior.coords))
            else:
                msp.add_lwpolyline(list(geom.exterior.coords), close=True)
                for interior in geom.interiors:
                    msp.add_lwpolyline(list(interior.coords), close=True)
                    
        elif hasattr(geom, 'geoms'):
            for part in geom.geoms:
                add_geom(part)

    for _, row in gdf.iterrows():
        add_geom(row.geometry)
        
    doc.saveas(output_path)

@app.post("/convertir")
async def convertir(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...), 
    epsg: str = Form(...),
    extract_attrs: bool = Form(True),
    export_shp: bool = Form(True),
    export_dxf: bool = Form(False)
):
    if not HAS_GEO:
        raise HTTPException(status_code=500, detail="Librerías geoespaciales no instaladas (geopandas/fiona).")
    
    if not (file.filename.endswith('.kml') or file.filename.endswith('.kmz')):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos .kml y .kmz")
    
    temp_dir = tempfile.mkdtemp()
    out_zip_path = os.path.join(tempfile.gettempdir(), f"output_{os.urandom(4).hex()}.zip")
    
    # Schedule cleanup
    background_tasks.add_task(cleanup_files, temp_dir, out_zip_path)
    
    try:
        input_path = os.path.join(temp_dir, file.filename)
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        kml_path = input_path
        if input_path.endswith('.kmz'):
            with zipfile.ZipFile(input_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
                for name in zip_ref.namelist():
                    if name.endswith('.kml'):
                        kml_path = os.path.join(temp_dir, name)
                        break
        
        try:
            gdf = gpd.read_file(kml_path, driver='KML')
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error leyendo KML: {str(e)}")
            
        if gdf.empty:
            raise HTTPException(status_code=400, detail="El archivo no contiene geometrías.")
            
        try:
            target_crs = f"EPSG:{epsg}"
            if gdf.crs:
                gdf = gdf.to_crs(target_crs)
            else:
                gdf.set_crs("EPSG:4326", inplace=True)
                gdf = gdf.to_crs(target_crs)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error reproyectando: {str(e)}")
            
        # Manejo de atributos
        if not extract_attrs:
            gdf = gdf[['geometry']]
        else:
            import pandas as pd
            import re
            
            def extract_html_table(desc):
                if not isinstance(desc, str): return {}
                data = {}
                trs = re.findall(r'<tr[^>]*>(.*?)</tr>', desc, re.IGNORECASE | re.DOTALL)
                for tr in trs:
                    cells = re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', tr, re.IGNORECASE | re.DOTALL)
                    if len(cells) >= 2:
                        key = re.sub(r'<[^>]+>', '', cells[0]).strip()
                        val = re.sub(r'<[^>]+>', '', cells[1]).strip()
                        if key and key.lower() not in ['name', 'description', 'descripción']:
                            data[key] = val
                return data

            if 'Description' in gdf.columns:
                extracted = gdf['Description'].apply(extract_html_table)
                extracted_df = pd.DataFrame(extracted.tolist())
                gdf = gdf.drop(columns=['Description'])
                gdf = pd.concat([gdf, extracted_df], axis=1)

            # --- Cálculo de Geometrías ---
            def calculate_geoms(row):
                geom = row.geometry
                res = {}
                if geom.geom_type == 'Point':
                    res['COORD_X'] = round(geom.x, 3)
                    res['COORD_Y'] = round(geom.y, 3)
                elif geom.geom_type in ['LineString', 'MultiLineString']:
                    res['PERIMETRO'] = round(geom.length, 2)
                elif geom.geom_type in ['Polygon', 'MultiPolygon']:
                    res['AREA'] = round(geom.area, 2)
                    res['PERIMETRO'] = round(geom.length, 2)
                    centroid = geom.centroid
                    res['CENTRO_X'] = round(centroid.x, 3)
                    res['CENTRO_Y'] = round(centroid.y, 3)
                return pd.Series(res)

            geom_stats = gdf.apply(calculate_geoms, axis=1)
            gdf = pd.concat([gdf, geom_stats], axis=1)
            # -----------------------------

            # Truncate attributes to 10 chars for DBF
            new_cols = []
            for col in gdf.columns:
                if col == 'geometry':
                    new_cols.append(col)
                else:
                    new_cols.append(str(col)[:10])
            gdf.columns = new_cols
        
        original_filename = os.path.splitext(file.filename)[0]
        output_name = original_filename
        
        shp_dir = os.path.join(temp_dir, "SHP")
        dxf_dir = os.path.join(temp_dir, "DXF")
        
        if export_shp:
            os.makedirs(shp_dir, exist_ok=True)
            out_shp = os.path.join(shp_dir, f"{output_name}.shp")
            gdf.to_file(out_shp)
            
        if export_dxf:
            os.makedirs(dxf_dir, exist_ok=True)
            out_dxf = os.path.join(dxf_dir, f"{output_name}.dxf")
            try:
                exportar_a_dxf(gdf, out_dxf)
            except Exception as e:
                print(f"Error exportando a DXF con ezdxf: {e}")
            
        with zipfile.ZipFile(out_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root_dir, _, files in os.walk(temp_dir):
                for file_name in files:
                    file_path = os.path.join(root_dir, file_name)
                    if file_path != input_path and file_path != kml_path:
                        arcname = os.path.relpath(file_path, temp_dir)
                        zipf.write(file_path, arcname=arcname)
                        
        return FileResponse(out_zip_path, media_type="application/zip", filename=f"{output_name}.zip")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/convertir-a-kml")
async def convertir_a_kml(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...)
):
    if not HAS_GEO:
        raise HTTPException(status_code=500, detail="Librerías geoespaciales no instaladas (geopandas/fiona).")
    
    if not files:
        raise HTTPException(status_code=400, detail="No se subieron archivos.")

    temp_dir = tempfile.mkdtemp()
    
    # Save all uploaded files to temp_dir
    file_paths = []
    for f in files:
        if f.filename:
            file_path = os.path.join(temp_dir, f.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(f.file, buffer)
            file_paths.append(file_path)
            
    # Extract ZIP files if any
    extracted_shps = []
    for fp in file_paths:
        if fp.lower().endswith('.zip'):
            with zipfile.ZipFile(fp, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
                for name in zip_ref.namelist():
                    if name.lower().endswith('.shp'):
                        extracted_shps.append(os.path.join(temp_dir, name))
        elif fp.lower().endswith('.shp'):
            extracted_shps.append(fp)

    if not extracted_shps:
        background_tasks.add_task(cleanup_files, temp_dir)
        raise HTTPException(status_code=400, detail="No se encontraron archivos .shp válidos.")

    import simplekml
    kml = simplekml.Kml()
    
    out_kmz_path = os.path.join(tempfile.gettempdir(), f"output_{os.urandom(4).hex()}.kmz")
    background_tasks.add_task(cleanup_files, temp_dir, out_kmz_path)
    
    try:
        from pyproj import CRS
        import pandas as pd
        import geopandas as gpd
        
        for shp_path in extracted_shps:
            layer_name = os.path.splitext(os.path.basename(shp_path))[0]
            try:
                gdf = gpd.read_file(shp_path)
            except Exception as e:
                print(f"Error leyendo {shp_path}: {e}")
                continue
                
            if gdf.empty:
                continue
                
            # Reproject to WGS84
            if gdf.crs:
                target_crs = CRS.from_epsg(4326)
                gdf = gdf.to_crs(target_crs)
            else:
                gdf.set_crs(epsg=4326, inplace=True)
            
            fol = kml.newfolder(name=layer_name)
            
            for _, row in gdf.iterrows():
                geom = row.geometry
                if geom is None or geom.is_empty:
                    continue
                
                # Fetch attributes (exclude geometry)
                attrs = {col: str(row[col]) for col in gdf.columns if col != 'geometry' and pd.notna(row[col])}
                desc_html = "<table border='1'>"
                for k, v in attrs.items():
                    desc_html += f"<tr><td><b>{k}</b></td><td>{v}</td></tr>"
                desc_html += "</table>"

                def extract_coords(g):
                    try:
                        return list(g.coords)
                    except:
                        return []

                def add_element(g, folder):
                    if g.geom_type == 'Point':
                        pnt = folder.newpoint(coords=extract_coords(g))
                        pnt.description = desc_html
                    elif g.geom_type == 'LineString':
                        lin = folder.newlinestring(coords=extract_coords(g))
                        lin.description = desc_html
                    elif g.geom_type == 'Polygon':
                        pol = folder.newpolygon(outerboundaryis=extract_coords(g.exterior))
                        if g.interiors:
                            pol.innerboundaryis = [extract_coords(i) for i in g.interiors]
                        pol.description = desc_html
                    elif g.geom_type in ['MultiPoint', 'MultiLineString', 'MultiPolygon', 'GeometryCollection']:
                        if hasattr(g, 'geoms'):
                            for part in g.geoms:
                                add_element(part, folder)
                
                add_element(geom, fol)

        kml.savekmz(out_kmz_path)
        
        output_name = "Converted_Layers"
        if len(extracted_shps) == 1:
            output_name = os.path.splitext(os.path.basename(extracted_shps[0]))[0]

        return FileResponse(out_kmz_path, media_type="application/vnd.google-earth.kmz", filename=f"{output_name}.kmz")

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
