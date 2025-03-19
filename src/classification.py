from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QHBoxLayout, QLabel
import matplotlib.pyplot as plt
import sys
import subprocess
import argparse
import geopandas as gpd
import numpy as np
import rasterio
from rasterio.features import rasterize
import matplotlib
matplotlib.use('Qt5Agg')
import json


def cut_shapefile(shapefile: str, cut: str, save: str = ""):
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
    shapes = [(geom, value)
              for geom, value in zip(vector.geometry, vector[column])]
    vector[column] = vector[column].fillna(0)
    raster = rasterize(
        shapes,
        out_shape=(height, width),
        transform=rasterio.transform.from_bounds(
            minx, miny, maxx, maxy, width, height),
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
        transform=rasterio.transform.from_bounds(
            minx, miny, maxx, maxy, width, height),
    ) as dst:
        dst.write(raster, 1)


def view(elem: str):
    if elem[len(elem)-3:] == "shp":
        class ShapefileViewer(QMainWindow):
            def __init__(self, shape):
                super().__init__()
                self.setWindowTitle("Shapefile Viewer")
                self.setGeometry(100, 100, 1000, 600)
                layout = QHBoxLayout()

                # Plot the shapefile and save to an image
                plt.figure()
                shape.plot()
                plt.title("Shapefile View")
                plt.savefig("shapefile_view.png")
                plt.close()

                # Add shapefile view
                pixmap = QPixmap("shapefile_view.png")
                shapefile_label = QLabel()
                shapefile_label.setPixmap(pixmap)
                shapefile_label.setAlignment(Qt.AlignCenter)
                layout.addWidget(shapefile_label)

                # Add attribute table
                self.table = QTableWidget()
                self.table.setRowCount(len(shape))
                self.table.setColumnCount(len(shape.columns))
                self.table.setHorizontalHeaderLabels(shape.columns)
                for i, row in shape.iterrows():
                    for j, col in enumerate(shape.columns):
                        self.table.setItem(
                            i, j, QTableWidgetItem(str(row[col])))
                layout.addWidget(self.table)

                container = QWidget()
                container.setLayout(layout)
                self.setCentralWidget(container)

        shape = gpd.read_file(elem)
        app = QApplication(sys.argv)
        viewer = ShapefileViewer(shape)
        viewer.show()
        sys.exit(app.exec_())
    elif elem[len(elem)-3:] == "tif":
        with rasterio.open(elem) as dataset:
            band = dataset.read(1)

            nodata_value = dataset.nodata if dataset.nodata is not None else 0

            band = np.ma.masked_equal(band, nodata_value)

            plt.imshow(band, cmap="viridis", vmin=band.min(), vmax=band.max())
            plt.colorbar()
            plt.title("raster view")
            plt.show()


def classification(tif: str, save: str, classify: str):
    with rasterio.open(tif) as dataset:
        band = dataset.read(1)

        reclassified = np.zeros_like(band)
        out_json = []
        
        if classify.isdigit():
            classify = int(classify)
            
            increment = 0
            while(classify * increment < band.max()):
                reclassified[(band >= classify * increment) & (band < classify*(increment+1))] = increment
                out_json.append({"value_min" : classify*increment , "value_max" : classify*(increment+1) , "value" : increment})
                increment += 1
                
            plt.imshow(reclassified, cmap='viridis')
            plt.colorbar()
            plt.title('Raster reclassifié')
            plt.show()
                
            profile = dataset.profile
            if save != "":
                with rasterio.open(save, 'w' , **profile) as out_data :
                    out_data.write(reclassified, 1)
            else :
                path = f"{'/'.join(tif.split("\\")[:-1])}/reclassify.tif"
                with rasterio.open(path, 'w' , **profile) as out_data :
                    out_data.write(reclassified, 1)
                    with open(f"{'/'.join(tif.split("\\")[:-1])}/config.json", 'w') as json_file:
                        json.dump(out_json, json_file)
            
        else:
            try:
                classify = [int(e) for e in classify.split(",")]
                print(classify)
                recup = 0
                for e in range(len(classify)-1):
                    reclassified[(band >= classify[e]) & (band < classify[e+1])] = e
                    out_json.append({"value_min" : classify[e] , "value_max" : classify[e+1] , "value" : e})
                    recup = e
                reclassified[(band >= classify[recup+1])] = recup+1
                out_json.append({"value_min" : classify[recup+1] , "value_max" : -1, "value" : recup+1})

                plt.imshow(reclassified, cmap='viridis')
                plt.colorbar()
                plt.title('Raster reclassifié')
                plt.show()
                
                profile = dataset.profile
                if save != "":
                    with rasterio.open(save, 'w' , **profile) as out_data :
                        out_data.write(reclassified, 1)
                else :
                    path = f"{'/'.join(tif.split("\\")[:-1])}/reclassify.tif"
                    with rasterio.open(path, 'w' , **profile) as out_data :
                        out_data.write(reclassified, 1)
                        with open(f"{'/'.join(tif.split("\\")[:-1])}/config.json", 'w') as json_file:
                            json.dump(out_json, json_file)
            except:
                raise Exception(
                    "Type de donnée non valide, si vous avez mis un liste, elle ce construit comme suit : 1,2,3,...")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Operation shapefile et raster pour nb-das")
    parser.add_argument("--view", help="Afficher un shapefile")
    parser.add_argument(
        "--shp", help="traitement d'un fichier shapefile (.shp)")
    parser.add_argument("--cut", help="Coupe le shapefile")
    parser.add_argument(
        "--save", default="", help="define the directory and the name of the saved result")
    parser.add_argument("--rasterize", default=False,
                        help="rasterize the shapefile")
    parser.add_argument("--col", help="column to rasterize")
    parser.add_argument("--resolution", default=0.1,
                        help="define resolution of the raster")
    parser.add_argument(
        "--raster", help="Utilisation d'un raster dans les géotraitement")
    parser.add_argument(
        "--classify", help="Classifciation du raster de deux manière différente")

    args = parser.parse_args()

    if (args.rasterize != False and args.col == None):
        raise Exception(
            "You can't rasterize without define column to rasterize")
    if (args.rasterize == False and args.col != None):
        raise Exception(
            "Argument column is used to rasterize, thanks to implement the --rasterize [file] in your command line")
    if args.classify != None and args.raster == None:
        raise Exception(
            "Vous ne pouvez pas classifier les vide (utiliser le flag --raster avant d'utiliser ce flag)")

    if (args.shp != None):
        if args.cut != None:
            cut_shapefile(args.shp, args.cut, args.save)
        if args.rasterize != False and args.col != None:
            rasterizer(args.shp, args.col, args.resolution, args.save)
    if (args.view != None):
        view(args.view)
    if args.classify != None:
        classification(args.raster, args.save, args.classify)
