import rasterio
import numpy as np

def calculate_raster_percentages(input_raster, output_raster=None):
    # Ouvrir le raster
    with rasterio.open(input_raster) as src:
        raster_data = src.read(1)  # Lecture de la première bande
        nodata = src.nodata

        # Masquer les valeurs nodata si elles existent
        if nodata is not None:
            valid_data = raster_data[raster_data != nodata]
        else:
            valid_data = raster_data

        # Calculer le pourcentage
        total_pixels = valid_data.size
        unique_values, counts = np.unique(valid_data, return_counts=True)
        percentages = (counts / total_pixels) * 100

        # Affichage des résultats
        print("Valeur | Pourcentage")
        print("--------------------")
        for value, percentage in zip(unique_values, percentages):
            print(f"{value}    | {percentage:.2f}%")

        # Sauvegarder le raster de pourcentage si demandé
        if output_raster:
            percentage_map = np.zeros_like(raster_data, dtype=np.float32)
            for value, percentage in zip(unique_values, percentages):
                percentage_map[raster_data == value] = percentage

            profile = src.profile
            profile.update(dtype=rasterio.float32)
            with rasterio.open(output_raster, 'w', **profile) as dst:
                dst.write(percentage_map, 1)

if __name__ == "__main__":
    input_raster = "./Raster/AGR/FINAL_RASTER/SILT_CONTENT.tif"
    output_raster = "./Raster/AGR/FINAL_RASTER/SILT_CONTENT_1.tif"  # Optionnel

    calculate_raster_percentages(input_raster, output_raster)
