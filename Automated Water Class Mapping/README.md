# Automated Water Classification Analysis

A two-step Python pipeline for extracting and analyzing water class data using Google Earth Engine (GEE) and local processing.

## 🔧 Prerequisites
- Python 3.7+
- Google Earth Engine account (authenticated)
- Required packages:
  ```bash
  pip install earthengine-api geopandas rasterio numpy matplotlib
  
## 🚀 Quick Start
1. **First, run the data export script** (`water_data_extraction.py`) to:
   - Fetch watershed boundaries from GEE
   - Export water class raster (JRC dataset)
   - Save outputs to your Google Drive
2. **Then run the analysis script** (`water_classification.py`) to:
   - Calculate water class statistics
   - Generate a visualization map
  
⏳ Alternative: Use Pre-Downloaded Data
For quick testing, use the included pre_downloaded_data.zip containing sample outputs from Step 1 (Denver watershed).
