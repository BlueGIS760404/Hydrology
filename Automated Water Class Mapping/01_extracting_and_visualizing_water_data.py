import ee
import geopandas as gpd
import rasterio
from rasterio.mask import mask
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

# Initialize the Earth Engine module
try:
    ee.Initialize()
except Exception as e:
    print("Error initializing Earth Engine. Please authenticate using ee.Authenticate().")
    raise e

# Define a region of interest (e.g., a specific watershed near Denver)
# Find valid HUC10 codes near Denver (-105, 39.7)
huc_id = '1019000101'  # Replace with a valid HUC10 code (e.g., from GEE Code Editor)
watershed = ee.FeatureCollection('USGS/WBD/2017/HUC10') \
    .filter(ee.Filter.eq('huc10', huc_id))

# Check if the watershed FeatureCollection is not empty
watershed_size = watershed.size().getInfo()
if watershed_size == 0:
    print(f"No watershed found for HUC10 code: {huc_id}. Using fallback geometry.")
    # Fallback to a rectangular geometry near Denver, Colorado
    watershed_geometry = ee.Geometry.Rectangle([-105.5, 39.5, -104.5, 40.5])
    watershed = ee.FeatureCollection([ee.Feature(watershed_geometry, {'name': 'fallback_region'})])
    print("Fallback geometry set: Rectangle near Denver, CO ([-105.5, 39.5, -104.5, 40.5]).")
else:
    print(f"Found {watershed_size} watershed(s) for HUC10 code: {huc_id}")
    watershed_geometry = watershed.geometry()

# Export the watershed boundary (or fallback geometry) as a shapefile to Google Drive
watershed_export_task = ee.batch.Export.table.toDrive(
    collection=watershed,
    description='watershed_boundary_huc10',
    fileFormat='SHP'
)
watershed_export_task.start()
print("Started export task for watershed boundary shapefile to Google Drive.")

# Load the water class dataset (reverting to original proxy)
water_data = ee.Image('JRC/GSW1_4/YearlyHistory/2020').select('waterClass')

# Clip the raster to the watershed boundary
try:
    clipped_nitrate = water_data.clip(watershed_geometry)
except Exception as e:
    print("Error during clipping:", str(e))
    raise e

# Export the clipped raster to Google Drive
raster_export_task = ee.batch.Export.image.toDrive(
    image=clipped_nitrate,
    description='water_class_raster',
    scale=30,  # Resolution in meters
    region=watershed_geometry,
    maxPixels=1e9,
    fileFormat='GeoTIFF'
)
raster_export_task.start()
print("Started export task for water class raster to Google Drive.")

# Local processing after downloading files from Google Drive
def process_local_files(watershed_shp, water_class_tif):
    # Load watershed shapefile
    watershed_gdf = gpd.read_file(watershed_shp)
    
    # Load water class raster
    with rasterio.open(water_class_tif) as src:
        water_class_data, water_class_transform = mask(src, watershed_gdf.geometry, crop=True)
        water_class_data = water_class_data[0]  # Assuming single band raster
    
    # Mask invalid data (e.g., NoData values)
    valid_data = np.ma.masked_invalid(water_class_data)
    
    # Calculate basic statistics
    mean_value = np.nanmean(valid_data)
    std_value = np.nanstd(valid_data)
    min_value = np.nanmin(valid_data)
    max_value = np.nanmax(valid_data)
    
    # Print results
    print(f"Mean Water Class Value: {mean_value:.2f}")
    print(f"Standard Deviation: {std_value:.2f}")
    print(f"Min Value: {min_value:.2f}")
    print(f"Max Value: {max_value:.2f}")
    
    # Create map with legend
    plt.figure(figsize=(10, 8))
    img = plt.imshow(water_class_data, cmap='viridis', extent=[
        water_class_transform[2], water_class_transform[2] + water_class_transform[0] * water_class_data.shape[1],
        water_class_transform[5] + water_class_transform[4] * water_class_data.shape[0], water_class_transform[5]
    ])
    plt.colorbar(img, label='Water Class (0-3)')
    
    # Plot watershed boundary
    watershed_gdf.boundary.plot(ax=plt.gca(), color='red', linewidth=2)
    
    # Add legend for watershed boundary
    legend_elements = [Patch(facecolor='none', edgecolor='red', linewidth=2, label='Watershed Boundary')]
    plt.legend(handles=legend_elements, loc='upper right')
    
    plt.title('Water Class Distribution in Watershed')
    plt.xlabel('Easting (m)')
    plt.ylabel('Northing (m)')
    plt.savefig('water_class_distribution_map.png')
    plt.close()
