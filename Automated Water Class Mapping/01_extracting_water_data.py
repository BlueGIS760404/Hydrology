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
    clipped_watershed = water_data.clip(watershed_geometry)
except Exception as e:
    print("Error during clipping:", str(e))
    raise e

# Export the clipped raster to Google Drive
raster_export_task = ee.batch.Export.image.toDrive(
    image=clipped_watershed,
    description='water_class_raster',
    scale=30,  # Resolution in meters
    region=watershed_geometry,
    maxPixels=1e9,
    fileFormat='GeoTIFF'
)
raster_export_task.start()
print("Started export task for water class raster to Google Drive.")
