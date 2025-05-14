import rasterio
from rasterio.mask import mask
import geopandas as gpd
import os
import argparse
import glob
import json


def cleanse(folder):
    files = glob.glob(folder + "*")
    for file in files:
        os.remove(file)


def value_sum(values: dict) -> int:
    return sum([v for k, v in values.items()])


def calc_value_percent(values: dict) -> dict:
    result = {}
    somme = value_sum(values)
    for k, v in values.items():
        result[k] = round(v * 100 / somme, 2)
    return result


def value_to_code(stats: dict, json_file, index: int) -> dict:
    result = {}
    for e in json_file["configurations"][index]["data"]["legend"]["details"]:
        if str(float(e["value"])) in stats:
            result[e["code"]] = stats[str(float(e["value"]))]
    print(stats)
    return result


def calculate_stats(src, json_file, index):
    data = src.read(1)
    height, width = data.shape
    stats = {}
    print(height, width)
    for row in range(height):
        for col in range(width):
            value = data[row, col]
            if str(value) in stats:
                stats[str(value)] += 1
            else:
                stats[str(value)] = 1
    
    return (value_to_code(stats, json_file, index))


def cutter(raster, shapefile: str, savefile: str = "", json_file: str = ""):
    tmp_file = "tmp_"
    output_dir = "../tmp"
    categorie_code = ""
    title = ""
    index = 0
    out = {}
    out_with_code = {}
    print("ahah")
    raster_name = raster.split("\\")[-1]
    for e in range(len(json_file["configurations"])):
        if "chromaColors" in json_file["configurations"][e]["data"]["legend"]:
            categorie_code = json_file['configurations'][e]["code"]
            return []
        if "path" in json_file['configurations'][e]["data"]:
            if json_file['configurations'][e]["data"]["path"].split("/")[-1] == raster_name:
                categorie_code = json_file['configurations'][e]["code"]
                title = json_file['configurations'][e]["name"]
                index = e
                break

    src = rasterio.open(raster)
    gdf = gpd.read_file(shapefile)

    gdf = gdf.to_crs(src.crs)

    os.makedirs(output_dir, exist_ok=True)

    for idx, row in gdf.iterrows():
        geometries = [row['geometry']]
        code = row['CODE']
        out_image, out_transform = mask(src, geometries, crop=True)

        out_meta = src.meta.copy()
        out_meta.update({
            "driver": "GTiff",
            "height": out_image.shape[1],
            "width": out_image.shape[2],
            "transform": out_transform
        })

        output = os.path.join(output_dir, f"{tmp_file}{code}.tif")
        with rasterio.open(output, "w", **out_meta) as dest:
            dest.write(out_image)
            print(
                f"Raster créer avec succès et enregistré dans : {output_dir}/{tmp_file}{code}.tif ✔️")
        with rasterio.open(output) as dest:
            out[code] = calc_value_percent(
                calculate_stats(dest, json_file, index))
    return ({"data": out, "code": categorie_code})


def raster_cutter(raster, shapefile: str, savefile: str = "", json_file: str = ""):

    json_output = {}

    with open(json_file, 'r', encoding='utf-8') as file:
        data = json.load(file)
        if type(raster) == str:
            cutter(raster, shapefile, savefile, data)
        if type(raster) == list:
            for tif in raster:

                out = cutter(tif, shapefile, savefile, data)
                
                print(f"{tif}  -  {out}")
                if len(out) == 0:
                    continue
                out_data = out["data"]
                out_code = out["code"]
                for key, value in out_data.items():
                    if key in json_output:
                        json_output[key].append(
                            {"code": out_code, "data": value})
                    else:
                        json_output[key] = [{
                            "code": out_code,
                            "data": {
                                "type": "static",
                                "legend": {
                                    "type": "singleValue",
                                    "title": out_code.lower().replace("_", " "),
                                    "details": [{"code" : e , "percentage" : i} for e , i in value.items()]
                                    }}}]
        if os.path.exists(savefile) == False:
            os.makedirs(savefile)
        for key, value in json_output.items() :
            with open(f"{savefile}{key}.json", "w") as json_file:
                json.dump({"configuration" : value},json_file)
                print("Fichier de configuration créer avec susccès")
            


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--shapefile", help="use this flag to define the shapefile which will be used to calculate statistics of raster")
    parser.add_argument("--raster_folder",
                        help="Use this flag to define the raster folder")
    parser.add_argument("--raster", help="Use this flag to define the raster")
    parser.add_argument(
        "--save_folder", help="Use this flag to set where the result will output")
    parser.add_argument("--tmp", help="define temp folder")
    parser.add_argument("--cleanse", help="Clear all file from a folder")
    parser.add_argument(
        "--json", help="define json where code is write (Only for DAS)")

    args = parser.parse_args()

    if args.json == None:
        raise ValueError(
            "You have to enter a valid path of json with '--json' and a valid path for the json output with '--save_folder'")
    if args.shapefile == None and (args.raster != None or args.raster_folder != None):
        raise ValueError("You have to define a shapefile to cut raster")

    raster = args.raster
    if args.raster_folder != None:
        raster = glob.glob(args.raster_folder + "/*.tif")

    if args.cleanse != None:
        cleanse(args.cleanse)
        print("Tout les fichiers on été supprimer ✔️")
        exit(0)

    raster_cutter(raster, args.shapefile, args.save_folder, json_file=args.json)
