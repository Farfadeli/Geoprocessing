import os
import glob

files = glob.glob("./raster/ENV/*/*.tif")

for file in files :
    filename = file.split("\\")[-1][:-4] + "_01.tif"
    file_path = file.split("\\")[0] + "/" + file.split("\\")[1] + "/" + filename
    
    print(file)
    
    os.system(f"gdal_translate -projwin 11 32 50 -16 -projwin_srs EPSG:4326 {file} {file_path} -of COG -co BLOCKSIZE=256")
