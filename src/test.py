import os
os.environ['GDAL_DATA'] = r'C:\Users\ndaunac\AppData\Local\miniconda3\envs\gdal_env\Library\share\gdal'
os.environ['PROJ_LIB'] = r'C:\Users\ndaunac\AppData\Local\miniconda3\envs\gdal_env\Library\share\proj'

from osgeo import gdal
print(gdal.VersionInfo())