import os
import sys
import glob
import fiona
import rasterio
from rasterio.mask import mask
import numpy as np
import json

"""
    cmd : python percent.py args
    args[0] = script_name
    args[1] = raster_folder
    args[2] = json folder
    args[3] = Country / Large / Small
"""
if (len(sys.argv) < 4):
    exit(1, "Il manque des paramètre afin qu l'application s'exécute correctement")

SHAPEFILE_FOLDER = "./Shapefile/BASE/"
if sys.argv[3].lower() == "country":
    SHAPEFILE_FOLDER = "./Shapefile/BASE/COUNTRY/limit.shp"
    col = "CODE"
if (sys.argv[3].lower() == "large"):
    SHAPEFILE_FOLDER = "./Shapefile/BASE/LARGE_BASIN/limit.shp"
    col = "code"
if (sys.argv[3].lower() == "small"):
    SHAPEFILE_FOLDER = "./Shapefile/BASE/SMALL_BASIN/limit.shp"
    col = "code"


def raster_analytic(feature, raster):
    with rasterio.open(raster) as raster_src:
        data = {}
        raster_data = raster_src.read(1)
        unique_value = np.unique(raster_data)
        raster_with_no_value = False

        if (len(unique_value) > 25):
            data = {"code": raster.split("/")[-1].split("\\")
             [-1][:-4], "data": {"type": "static"}}
            raster_with_no_value = True

        if raster_with_no_value:
            return (data)

        data = {"code": raster.split("/")[-1].split("\\")[-1][:-4], "data": {"type": "static", "legend": {"type": "singleValue"}}}

        geometry = [feature["geometry"]]
        name = feature["properties"].get(col, "Unknown")

        out_image, out_transform = mask(
            raster_src, geometry, crop=True, nodata=raster_src.nodata)

        raster_values = out_image[0].flatten()
        raster_values = raster_values[raster_values != raster_src.nodata]

        unique, counts = np.unique(raster_values, return_counts=True)
        total_pixels = np.sum(counts)
        percentages = {int(u): (c / total_pixels) *
                       100 for u, c in zip(unique, counts)}

        title = raster.split(
            "/")[-1].split("\\")[-1][:-4].replace("_", " ").lower()
        details = []
        for key, value in percentages.items():
            details.append(
                {"code": str(key), "percentage": round(value.item(), 2)})
        data["data"]["legend"]["title"] = title
        data["data"]["legend"]["details"] = details

        return (data)



def get_features(folder: str):
    shapefile = fiona.open(SHAPEFILE_FOLDER)
    rasters = glob.glob(f"{sys.argv[1]}/*.tif")

    for feature in shapefile:
        data = {"configurations": []}

        for raster in rasters:
            data["configurations"].append(raster_analytic(feature, raster))

        with open(f"{sys.argv[2]}{feature["properties"].get(col).lower()}.json", "w") as new_file:
            json.dump(data, new_file)
            print("Fichier créer avec succès 🚀")


get_features(SHAPEFILE_FOLDER)
