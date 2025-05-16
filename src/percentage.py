import code
import os
import glob
import rasterio
from rasterio.mask import mask
import geopandas as gpd
import json
import argparse
import numpy as np

def read_json(json_file: str):
    with open(json_file, 'r', encoding="utf-8") as json_f:
        json_data = json.load(json_f)
        return json_data

def clean_tmp() :
    tmp_file = glob.glob("./tmp/*.tif")
    for e in tmp_file:
        os.remove(e)

def get_type(raster : str, json_file : str) -> str:
    """
        function permettant de retrouver le type raster en fonction de son nom
        Args:
            raster (str): raster qui est dans entire_nile.json
            json (str): entire_nile.json
        """
    json_data = read_json(json_file)

    for idx in range(len(json_data["configurations"])):
        elem = json_data["configurations"][idx]
        if "path" in elem["data"] :
            if os.path.basename(elem["data"]["path"]) == os.path.basename(raster):
                return elem["data"]["legend"]["type"]

def get_code(raster: str, json_file: str) -> str:
    """
    function permettant de retrouver le code de la catégorie en fonction du nom du raster
    Args:
        raster (str): raster qui est dans entire_nile.json
        json (str): entire_nile.json
    """
    json_data = read_json(json_file)

    for idx in range(len(json_data["configurations"])):
        elem = json_data["configurations"][idx]
        if "path" in elem["data"] :
            if os.path.basename(elem["data"]["path"]) == os.path.basename(raster):
                return elem["code"]

def get_categ_name(raster: str, json_file : str) -> str:
    json_data = read_json(json_file)

    for idx in range(len(json_data["configurations"])):
        elem = json_data["configurations"][idx]
        if "path" in elem["data"]:
            if os.path.basename(elem["data"]["path"]) == os.path.basename(raster):
                return elem["name"]

def get_json_part(raster : str, json_file : str):
    json_data = read_json(json_file)

    for idx in range(len(json_data["configurations"])):
        elem = json_data["configurations"][idx]
        if "path" in elem["data"]:
            if os.path.basename(elem["data"]["path"]) == os.path.basename(raster):
                return elem["data"]["legend"]["details"]

def create_tmp_raster(raster: str, shapefile: str):
    output_dir = "./tmp"
    raster_src = rasterio.open(raster)
    gdf = gpd.read_file(shapefile)

    gdf = gdf.to_crs(raster_src.crs)

    for idx, row in gdf.iterrows():
        geometries = [row["geometry"]]
        code = row["CODE"] if "Countries" in shapefile else row["code"]

        out_image, out_transform = mask(raster_src, geometries, crop=True)

        out_meta = raster_src.meta.copy()
        out_meta.update({
            "driver": "GTiff",
            "height": out_image.shape[1],
            "width": out_image.shape[2],
            "transform": out_transform
        })

        output = os.path.join(output_dir, f"{code}.tif")
        with rasterio.open(output, "w", **out_meta) as dest:
            dest.write(out_image)
            print(f"Raster créer avec succès et enregistré dans : {output_dir}/{code.lower()}.tif ✔️")

def get_code_idx(data, code):
    """
    Récupère l'index du code dans details de entire_nile retourne egalement si le code existe déjà dans le tableau
    :param data:
    :param code:
    :return:
    """
    for e in range(len(data)):
        if code in data[e]:
            return (True, e)
    return (False, -1)

def percent_array(data):
    """
    fonction qui défini le pourcentage de chaque valeur du raster à partir d'une liste de dictionnaire avec la quantité des valeurs
    :param data:
    :return:
    """

    somme = 0
    res = []
    for e in data:
        for key , value in e.items() : somme += value
    for i in range(len(data)):
        for key, value in data[i].items():
            res.append({key : round(value * 100 / somme,2)})
    return res

def get_percent(data):
    """
    Fonction qui retourne une liste pour chaque element du shapefile avec les pourcentage de chaque valeur du raster
    :param data:
    :return:
    """
    res = {}
    rep = {}

    for raster in glob.glob("./tmp/*.tif") :
        file_name = os.path.basename(raster)

        with rasterio.open(raster) as src:
            file_name = file_name[:-4]
            rep[file_name] = []

            band = src.read(1)
            h, w = band.shape

            for row in range(h):
                for col in range(w):
                    value = band[row, col]
                    code_value = [data[e]["code"] for e in range(len(data)) if data[e]["value"] == value]
                    if len(code_value) == 0 : continue
                    code = code_value[0]
                    is_set, idx = get_code_idx(rep[file_name], code)

                    if is_set :
                        rep[file_name][idx][code] += 1
                    else:
                        rep[file_name].append({code : 1})
                    rep[file_name] = percent_array(rep[file_name])
            res[file_name] = rep[file_name]
    return res

def save_conf_files(data, save):
    for key, value in data.items():
        with open(f"{save}/{key.lower()}.json", "w") as outfile:
            json.dump(value, outfile, indent=4)

def get_average():
    res = {}
    for raster in glob.glob("./tmp/*.tif") :

        with rasterio.open(raster) as src:
            file_name = os.path.basename(raster)[:-4]

            band = src.read(1)
            h, w = band.shape
            somme = np.int64(0)

            for row in range(h):
                for col in range(w):
                    value = band[row, col]
                    if(value > 0):
                        somme += band[row, col]
            avg = somme / (h * w)
            res[file_name] = round(float(avg), 2)
    return res

def general_controller(rasters: list, shapefile : str, json_file: str, save: str):
    """
        fonction utiliser comme une fonction main qui va appeller toutes les autres fonctions
    """
    final_json = {}

    for raster in rasters:
        raster_type = get_type(raster, json_file)
        raster_code = get_code(raster, json_file)
        raster_name = get_categ_name(raster, json_file)


        if raster_type == None : continue

        create_tmp_raster(raster, shapefile)

        # 2 type de raster possible ChromaColor(moyenne pixel) et SingleValue(pourcentage)
        if raster_type == "singleValue" :
            raster_data = get_json_part(raster, json_file)
            percent_array = get_percent(raster_data)
            for key, value in percent_array.items() :
                if key in final_json :
                    final_json[key]["configurations"].append({
                        "code" : raster_code,
                        "data" : {
                            "type" : "static",
                            "legend" : {
                                "type" : raster_type,
                                "title" : raster_name,
                                "details" : [{"code" : k , "percentage" : v} for elem in value for k , v in elem.items() ]
                            }
                        }
                    })
                else :
                    final_json[key] = {"configurations" : [{
                        "code" : raster_code,
                        "data" : {
                            "type" : "static",
                            "legend" : {
                                "type" : raster_type,
                                "title" : raster_name,
                                "details" : [{"code" : k , "percentage" : v} for elem in value for k , v in elem.items() ]
                            }
                        }
                    }]}

        if raster_type == "chromaColors" :
            average_array = get_average();
            for key, value in average_array.items() :
                if key in final_json :
                    final_json[key]["configurations"].append({
                        "code": raster_code,
                        "data": {
                            "type" : "static",
                            "analyticSingleValue" : round(value, 2)
                        }
                    })
                else:
                    final_json[key] = {"configurations": [{
                        "code": raster_code,
                        "data": {
                            "type" : "static",
                            "analyticSingleValue": round(value, 2)
                        }
                    }]}


    save_conf_files(final_json, save)


if __name__ == "__main__":
    """
    Argument ligne de commande :
        --rasters [dossier_raster]
        --shapefile [fichier .shp]
        --json [fichier json entire_nile]
        --save [dossier ou stocker les données]
    """
    # Ajout des arguments obligatoire pour faire fonctionner le script
    parser = argparse.ArgumentParser()

    parser.add_argument("--rasters", help="Choisir le dossier ou sont stocker tout les .tif")
    parser.add_argument("--shapefile", help="Choisir le fichier shapefile sur le quel faire les pourcentage")
    parser.add_argument("--json", help="choisir le fichier de configuration parents (entire_nile.json)")
    parser.add_argument("--save", help="choisir ou seront sortie les fichiers de configuration")

    args = parser.parse_args()

    # Gestion des erreurs dans les arguments passer au script
    if args.rasters == None or os.path.exists(args.rasters) == False:
        raise ValueError("Vous devez obligatoirement rentrée un argument --rasters valide")
    if args.shapefile == None or os.path.exists(args.shapefile) == False:
        raise ValueError("Vous devez obligatoirement rentrée un argument --shapefile valide")
    if args.json == None or os.path.exists(args.json) == False:
        raise ValueError("Vous devez obligatoirement rentrée un argument --json valide")
    if args.save == None : raise ValueError("Vous devez obligatoirement rentrée l'argument --save")

    # Création des fichier/dossier utile au bon déroulement du script
    if os.path.exists("./tmp") == False : os.mkdir("./tmp")
    if os.path.exists(args.save) == False : os.mkdir(args.save)

    general_controller(glob.glob(f"{args.rasters}/*.tif"), args.shapefile, args.json, args.save)

    clean_tmp()