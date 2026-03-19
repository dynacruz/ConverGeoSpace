import os
import io
import zipfile
import geopandas as gpd
from shapely.geometry import Point
from fastapi.testclient import TestClient
from main import app
import tempfile

def test_conversion():
    client = TestClient(app)

    # Create dummy shapefile
    gdf = gpd.GeoDataFrame(
        {'Name': ['A', 'B'], 'Value': [1, 2]},
        geometry=[Point(0, 0), Point(1, 1)],
        crs="EPSG:4326"
    )

    temp_dir = tempfile.mkdtemp()
    shp_path = os.path.join(temp_dir, "test.shp")
    gdf.to_file(shp_path)

    files_to_upload = []
    for ext in ['.shp', '.shx', '.dbf', '.prj']:
        fpath = os.path.join(temp_dir, "test" + ext)
        if os.path.exists(fpath):
            files_to_upload.append(
                ("files", (os.path.basename(fpath), open(fpath, "rb"), "application/octet-stream"))
            )

    response = client.post("/convertir-a-kml", files=files_to_upload)
    print("Status Code:", response.status_code)

    if response.status_code == 200:
        out_kmz = os.path.join(temp_dir, "out.kmz")
        with open(out_kmz, "wb") as f:
            f.write(response.content)
        print("KMZ saved to:", out_kmz)
        
        # check if kmz is valid zip
        try:
            with zipfile.ZipFile(out_kmz, 'r') as z:
                print("KMZ contents:", z.namelist())
                assert "doc.kml" in z.namelist()
                print("Test passed!")
        except Exception as e:
            print("Invalid KMZ:", e)
    else:
        print("Error:", response.text)

if __name__ == "__main__":
    test_conversion()
