import rasterio
from rasterio.mask import mask
import geopandas as gpd
import os
import argparse
import glob

def cleanse(folder):
    files = glob.glob(folder + "*")
    for file in files:
        os.remove(file)

def raster_cutter(raster, shapefile):
    tmp_file = "tmp_"
    output_dir = "../tmp"
    if type(raster) == str:
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
            with rasterio.open(output, "w" , **out_meta) as dest:
                dest.write(out_image)
                print(f"Raster créer avec succès et enregistré dans : {output_dir}/{tmp_file}{code}.tif ✔️")

    if type(raster) == list:
        print(raster)


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
    parser.add_argument("--json", help="define json where code is write (Only for DAS)")

    args = parser.parse_args()
    
    if args.shapefile == None and (args.raster != None or args.raster_folder != None) : raise ValueError("You have to define a shapefile to cut raster")
    
    raster = args.raster
    if args.raster_folder != None:
        raster = glob.glob(args.raster_folder + "/*.tif")

    if args.cleanse != None :
        cleanse(args.cleanse)
        print("Tout les fichiers on été supprimer ✔️")
        exit(0)
    
    raster_cutter(raster, args.shapefile)
