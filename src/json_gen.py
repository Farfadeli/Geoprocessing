import json
import sys
import random
import argparse
import rasterio
import numpy as np

parser = argparse.ArgumentParser(
        description="creation json nb-das")
parser.add_argument("--file" , help="path of config file")
parser.add_argument("--raster" , help="generate json with a raster")
parser.add_argument("--rasters", help="Folder where you have multiple raster to import")
parser.add_argument("--save" ,help="choose where you want to create the file")
parser.add_argument("--start", help="Début de la légende")
parser.add_argument("--mid", help="milieu de la légende")
parser.add_argument("--end", help="fin de la légende")

args = parser.parse_args()

# if(args.file != None) :

#     with open(args.file, 'r') as f:
#         json_file = json.load(f)
#         output = []
#         for e in json_file:
#             output.append({
#                 "code" : str(e["value"]),
#                 "color" : '#{:06x}'.format(random.randint(0, 0xFFFFFF)),
#                 "name" : (args.start if args.start != None else "") + str(e["value_min"]) + (args.mid if args.mid != None else "") + str(e["value_max"]) + (args.end if args.end != None else ""),
#                 "value" : e["value"],
#                 "percentage" : 0.0,
#                 "analyticValue": 0.0
#             })

#         with open(f"{'/'.join(args.file.split("\\")[:-1])}/CONF.json", "w") as out_file :
#             print(f"{'/'.join(args.file.split("\\")[:-1])}/CONF.json")
#             json.dump(output, out_file)

if(args.raster != None):
    with rasterio.open(args.raster) as dataset:
        # Lis les données du raster
        data = dataset.read(1)  # Lis la première bande (tu peux adapter si ton raster a plusieurs bandes)
        
        # Masque les valeurs "no data" si elles existent
        mask = data != dataset.nodata
        
        # Applique le masque pour éviter les valeurs no data dans les calculs
        data = data[mask]
        
        # Trouve la valeur minimum et maximum
        min_value = int(np.min(data))
        max_value = int(np.max(data))
        json_output = {"scale": ["#ffffff","#0000ff"],"domain": [min_value,max_value]}
        with open(f"{args.raster[:-4]}.json" , 'w') as json_file :
            json.dump(json_output, json_file)

