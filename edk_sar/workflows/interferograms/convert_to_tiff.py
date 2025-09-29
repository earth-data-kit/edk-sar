# 04_convert_to_tiff.py
# Purpose: convert all *_geo.vrt files into GeoTIFFs for visualization and export.

# What this file will do (step-by-step):
# 1) Load config.py values (BASE_DIR, list of *_geo.vrt files).
# 2) Expected inputs:
#    - cor_geo.vrt
#    - int_geo.vrt
#    - unw_geo.vrt
#    - conn-comp_geo.vrt
#    - phase_geo.vrt
#    - displacement_geo.vrt
# 3) For each file:
#    - Validate that file exists.
#    - Run gdal_translate to convert VRT -> .tif.
#    - Output pattern: <basename>.tif (e.g., int_geo.tif).
# 4) Sanity check: run gdalinfo on each .tif to confirm raster bands are written.

# This file will have a run() function:
# - Reads list of files from config.py.
# - Then executed from runner.py as convert_to_tiff.run().
