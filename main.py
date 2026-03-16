import os
import shutil
import tempfile
import zipfile
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

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

@app.post("/convertir")
async def convertir(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...), 
    epsg: str = Form(...)
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
            
        # Truncate attributes to 10 chars for DBF
        new_cols = []
        for col in gdf.columns:
            if col == 'geometry':
                new_cols.append(col)
            else:
                new_cols.append(col[:10])
        gdf.columns = new_cols
        
        output_name = "topografia_convertida"
        out_shp = os.path.join(temp_dir, f"{output_name}.shp")
        out_dxf = os.path.join(temp_dir, f"{output_name}.dxf")
        
        gdf.to_file(out_shp)
        try:
            gdf.to_file(out_dxf, driver="DXF")
        except Exception as e:
            print(f"Error DXF support missing: {e}")
            
        with zipfile.ZipFile(out_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root_dir, _, files in os.walk(temp_dir):
                for file_name in files:
                    file_path = os.path.join(root_dir, file_name)
                    if file_path != input_path and file_path != kml_path:
                        zipf.write(file_path, arcname=file_name)
                        
        return FileResponse(out_zip_path, media_type="application/zip", filename=f"{output_name}.zip")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
