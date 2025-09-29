# 05_convert_to_cog.py
# Purpose: convert all .tif files into COGs.

# What this file will do (step-by-step):
# 1) Load config.py values (BASE_DIR, list of .tif files).
# 2) Expected inputs:
#    - cor_geo.tif
#    - int_geo.tif
#    - unwrap_geo.tif
#    - connected-component_geo.tif
#    - phase_geo.tif
#    - displacement_geo.tif
# 3) For each file:
#    - Validate that file exists.
#    - Run gdal_translate with COG driver.
#    - Output pattern: <basename>.cog.tif (e.g., displacement_geo.cog.tif).
# 4) Sanity check: run gdalinfo on each .cog.tif to confirm COG structure.

# This file will have a run() function:
# - Reads list of files from config.py.
# - Then executed from runner.py as convert_to_cog.run().
