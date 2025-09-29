# 01_geocode_vrts.py
# Purpose: take the four input VRTs (cor/int/unwrap/concomm) and produce
# *_geo.vrt files that include geolocation metadata pointing to lon/lat VRTs.


# What this file will do (step-by-step):
# 1) Load config.py values (BASE_DIR, input VRT names, lon/lat VRTs).
# 2) Take input VRT files (cor.vrt, int.vrt, unwrap.vrt, connected-component.vrt).
# 3) For each input VRT:
# - Validate that file exists. If missing -> log error and stop.
# - Output filename pattern: <original_basename>_geo.vrt (e.g., int_geo.vrt).
# 4. Save geocoded outputs (cor_geo.vrt, int_geo.vrt, unwrap_geo.vrt, connected-component_geo.vrt).
# 5) Sanity checks after writing each *_geo.vrt:
# - Run `gdalinfo <file>` and assert that geolocation metadata fields exist.

# This file will have a run() function:
# - config values like DEM path, geocoding parameters will be read from config.py.
# - Then executed from runner.py as geocode_vrt.run().
