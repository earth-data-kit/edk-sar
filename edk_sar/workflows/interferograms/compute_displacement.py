# 03_compute_displacement.py
# Purpose: convert phase (phase_geo.vrt) into displacement (displacement_geo.vrt).

# What this file will do (step-by-step):
# 1) Load config.py values (BASE_DIR, radar wavelength lambda).
# 2) Check that phase_geo.vrt exists. If missing -> log error and stop.
# 3) Create a new VRT file displacement_geo.vrt:
#    - Formula: displacement = (lambda / (4 * pi)) * phase.
#    - Lambda value is read from config.py.
# 4) Output filename: displacement_geo.vrt.
# 5) Run `gdalinfo displacement_geo.vrt` and validate it is Float32 with displacement metadata.

# This file will have a run() function:
# - Uses config values for wavelength.
# - Then executed from runner.py as compute_displacement.run().
