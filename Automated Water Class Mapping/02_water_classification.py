import geopandas as gpd
import rasterio
from rasterio.mask import mask
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

# Note: This script assumes the raster is the waterClass data from JRC/GSW1_4/YearlyHistory/2020.
# Load watershed shapefile (assumed exported with a valid HUC10 code near Denver, e.g., from GEE)
watershed = gpd.read_file('watershed_boundary_huc10.shp')

# Load water class raster (originally from JRC dataset)
with rasterio.open('water_class_raster.tif') as src:
    # Clip raster to watershed boundary
    clipped_data, clipped_transform = mask(src, watershed.geometry, crop=True)
    water_class_data = clipped_data[0]  # Assuming single band raster

# Mask invalid data (e.g., NoData values)
water_class_data = np.ma.masked_invalid(water_class_data)

# Calculate statistics
mean_value = np.nanmean(water_class_data)
std_value = np.nanstd(water_class_data)
min_value = np.nanmin(water_class_data)
max_value = np.nanmax(water_class_data)

# Print results
print(f"Mean Water Class Value: {mean_value:.2f}")
print(f"Standard Deviation: {std_value:.2f}")
print(f"Min Value: {min_value:.2f}")
print(f"Max Value: {max_value:.2f}")

# Visualize water class distribution with continuous colormap
plt.figure(figsize=(10, 8))
im = plt.imshow(water_class_data, cmap='viridis', extent=[
    clipped_transform[2], clipped_transform[2] + clipped_transform[0] * water_class_data.shape[1],
    clipped_transform[5] + clipped_transform[4] * water_class_data.shape[0], clipped_transform[5]
])
plt.colorbar(im, label='Water Class (0-3)', ticks=[0, 1, 2, 3])
plt.title('Water Class Distribution in Watershed')
plt.xlabel('Easting (m)')
plt.ylabel('Northing (m)')

# Plot watershed boundary
watershed.boundary.plot(ax=plt.gca(), color='red', linewidth=2)

# Add legend for watershed boundary and water classes
water_class_legend = [
    Patch(facecolor=plt.cm.viridis(0.0), edgecolor=plt.cm.viridis(0.0), label='0: No water'),
    Patch(facecolor=plt.cm.viridis(0.33), edgecolor=plt.cm.viridis(0.33), label='1: Occasional Water'),
    Patch(facecolor=plt.cm.viridis(0.67), edgecolor=plt.cm.viridis(0.67), label='2: Seasonal water'),
    Patch(facecolor=plt.cm.viridis(1.0), edgecolor=plt.cm.viridis(1.0), label='3: Permanent water')
]
boundary_legend = [Patch(facecolor='none', edgecolor='red', linewidth=2, label='Watershed Boundary')]
plt.legend(handles=water_class_legend + boundary_legend, loc='upper right', bbox_to_anchor=(1.0, 1))

plt.savefig('water_class_distribution_map.png')
plt.close()
