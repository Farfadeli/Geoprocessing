# Geoprocessing
Geoprocesing can be used by everyone.

with this repo you can do a lot of geoprocessing like the repository name suggest 🙃

## Install
To install geoprocessing, you can do as follows :

<b>1. clone the repo with this command :</b>
```console
foo@bar:~$ git clone https://github.com/Farfadeli/Geoprocessing.git
```
<b>2.Create a 'command' folder in 'C:/'</b>

<b>3. Move 'classification.py' file into the folder</b>

<b>4. open terminal and do the below commands :</b>
```console
foo@bar:~$ notepad $PROFILE
```
In the notepad window, add this line :
```console
function geoprocessing { python "C:\command\classification.py" @args }
```
after this cloase notepad and run this command :
```console
foo@bar:~$ .$PROFILE
```
<b>You can now use the command in your terminal</b>

## How to use
After the install, you can normally use the command in your terminal :
```console
foo@bar:~$ geoprocessing
```

this command have a lot of arguments to do what you want.

### <b>Params</b>
<b>In the command line you can use the belows params :</b>

`--shp`, this flag can be used to define the fact that the data source is a shapefile. you must specify the location of the shapefile.

`--cut`, with this flag you can cut your shapefile, 
with this parameter you must put the location of the file with the shapefile to use for cutting.

`--save`, you can use this flag if you want to save your work in a specific directory, otherwise the data will overwrite the old data. specify the folder where you want to save and the name of the file.

`--rasterize True` this flag is used to rasterize a shapefile, this flag don't work without this flag :
`--col` wich is used to define the column to rasterize the shapefile.
the column must be of numeric type.
You can also use the flag `--resolution` with rasterize, this flag take a float value and is used to define the resolution of the final raster.