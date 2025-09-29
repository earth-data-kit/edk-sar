# 02_compute_phase.py
# Purpose: take geocoded interferogram (int_geo.vrt) and produce phase.vrt
# using GDAL PixelFunctionType="phase".

# What this file will do (step-by-step):
# 1) Load config.py values (BASE_DIR, int_geo.vrt path).
# 2) Check that int_geo.vrt exists. If missing -> log error and stop.
# 3) Create a new VRT file phase.vrt:
#    - Single band with <PixelFunctionType>Phase</PixelFunctionType>.
#    - Input is int_geo.vrt (complex).
# 4) Output filename: phase_geo.vrt.
# 5) Run `gdalinfo phase_geo.vrt` and validate that band type = Float32 and has Phase pixel function.

# This file will have a run() function:
# - It will read file paths from config.py.
# - Generate VRT with <PixelFunctionType>Phase</PixelFunctionType>.
# - Save as phase_geo.vrt.
# - Then executed from runner.py as compute_phase.run().
