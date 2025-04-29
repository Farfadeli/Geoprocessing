import xarray as xr
import rasterio
from rasterio.transform import from_origin
import glob
import os
from osgeo import gdal

def correct_georeferencing(nc_file, tif_file):
    """
    Convertit un fichier .nc en .tif avec une projection correcte (EPSG:4326)
    et ajuste l'étendue si nécessaire.
    """
    # Utiliser gdal_translate pour convertir le fichier NetCDF (.nc) en GeoTIFF (.tif)
    command = f"gdal_translate -a_srs EPSG:4326 -of GTiff {nc_file} {tif_file}"
    os.system(command)
    
    # Vérification des métadonnées du fichier de sortie
    dataset = gdal.Open(tif_file)
    if dataset is None:
        print(f"Erreur lors de l'ouverture du fichier {tif_file}.")
        return
    
    # Obtenir les informations de géoréférencement
    geotransform = dataset.GetGeoTransform()
    print("Géotransformation avant correction :")
    print(f"Origin (ulx, uly): ({geotransform[0]}, {geotransform[3]})")
    print(f"Pixel Size (x, y): ({geotransform[1]}, {geotransform[5]})")
    
    # Si les coordonnées sont incorrectes (par exemple, la longitude et latitude sont inversées)
    if geotransform[0] < -180 or geotransform[0] > 180:
        # Corriger les coordonnées du coin supérieur gauche (origin)
        corrected_geotransform = (-180, 0.5, 0, 90, 0, -0.5)
        dataset.SetGeoTransform(corrected_geotransform)
        print("Géoréférencement corrigé avec succès.")

        # Sauvegarder la correction dans un nouveau fichier
        driver = gdal.GetDriverByName('GTiff')
        corrected_dataset = driver.CreateCopy(f"{tif_file.replace('.tif', '_corrected.tif')}", dataset)
        corrected_dataset = None
        print(f"Fichier corrigé enregistré sous {tif_file.replace('.tif', '_corrected.tif')}.")
    
    dataset = None


nc_files = glob.glob("./NC/ENV/BIO/*.nc")

for nc_file in nc_files :
    
    
    num_bio = nc_file.split("\\")[1][:5]
    
    os.makedirs(f"./raster/ENV/{num_bio}")
    shp_file = f"./raster/ENV/{num_bio}/{num_bio}.tif"
    
        
    
    correct_georeferencing(nc_file, shp_file)
