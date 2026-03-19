@echo off
echo Construyendo el ejecutable de ConverGeoSpace...
pyinstaller --name ConverGeoSpace --noconfirm --add-data "static;static" --collect-all uvicorn --collect-all geopandas --collect-all fiona --collect-all pyproj --collect-all shapely --collect-all ezdxf --hidden-import python-multipart -w main.py
echo Construccion completada.
pause
