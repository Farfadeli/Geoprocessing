import sys
import subprocess
import argparse
import geopandas as gpd
import numpy as np
import rasterio
from rasterio.features import rasterize


def cut_shapefile(shapefile: str,cut: str, save: str = ""):
    shp = gpd.read_file(shapefile)
    cut = gpd.read_file(cut)

    coupe = gpd.overlay(shp, cut, how='intersection')

    coupe.to_file(shapefile) if save == "" else coupe.to_file(save)

    print("Découpage de la couche vectorielle terminer")


def rasterizer(shp: str, column: str, resolution: float, save: str = ""):
    vector = gpd.read_file(shp)

    
    minx, miny, maxx, maxy = vector.total_bounds
    width = int((maxx - minx) / resolution)
    height = int((maxy - miny) / resolution)
    
    raster = np.zeros((height, width), dtype=np.uint8)
    shapes = [(geom, value) for geom, value in zip(vector.geometry, vector[column])]
    
    vector[column] = vector[column].fillna(0)
    
    raster = rasterize(
        shapes,
        out_shape=(height, width),
        transform=rasterio.transform.from_bounds(minx, miny, maxx, maxy, width, height),
        fill=0,
        dtype='float32'
    )
    
    with rasterio.open(
        ("output_raster.tif" if save == "" else save),
        'w',
        driver='GTiff',
        height=height,
        width=width,
        count=1,
        dtype=raster.dtype,
        crs=vector.crs,
        transform=rasterio.transform.from_bounds(minx, miny, maxx, maxy, width, height),
    ) as dst:
        dst.write(raster, 1)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Operation shapefile et raster pour nb-das")
    parser.add_argument("--shp", help="traitement d'un fichier shapefile (.shp)")
    parser.add_argument("--cut", help="Coupe le shapefile")
    parser.add_argument("--save", default="", help="define the directory and the name of the saved result")
    parser.add_argument("--rasterize", default= False, help="rasterize the shapefile")
    parser.add_argument("--col", help="column to rasterize")
    parser.add_argument("--resolution", default=0.1, help="define resolution of the raster")

    args = parser.parse_args()

    if (args.rasterize != False and args.col == None):raise Exception("You can't rasterize without define column to rasterize")
    if (args.rasterize == False and args.col != None):raise Exception("Argument column is used to rasterize, thanks to implement the --rasterize [file] in your command line")

    if (args.shp != None):
        if args.cut != None: cut_shapefile(args.shp, args.cut, args.save)
        if args.rasterize != False and args.col != None: rasterizer(args.shp, args.col , args.resolution, args.save)
