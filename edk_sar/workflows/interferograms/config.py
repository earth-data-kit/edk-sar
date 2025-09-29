# config.py
# Purpose: centralize all configuration values for the EDK-SAR workflow.
# Any file in the workflow reads these values instead of hardcoding paths or parameters.

# 1) BASE_DIR = "/path/to/edk-sar/data/stack/merged/interferograms/20180830_20181228/"

# 2) INPUT_VRT_NAMES
# Paths to input VRTs (relative to BASE_DIR or absolute)
# COR_VRT = BASE_DIR + "cor.vrt"
# INT_VRT = BASE_DIR + "int.vrt"
# UNWRAP_VRT = BASE_DIR + "unw.vrt"
# CONNECTED_VRT = BASE_DIR + "conncomp.vrt"

# Geolocation grid VRTs
# LON_VRT = BASE_DIR + "geom_reference/lon.rdr.full.vrt"
# LAT_VRT = BASE_DIR + "geom_reference/lat.rdr.full.vrt"

# Output directory
# - Directory where all intermediate and final outputs (VRT, TIFF, COG) are stored.
# OUTPUT_DIR = BASE_DIR + "outputs/"

# 5) RADAR_WAVELENGTH
# - Wavelength of radar in meters (lambda).
# - Used in displacement computation.


# 6) TIFF_PARAMS
# - Parameters for gdal_translate to convert VRT -> TIFF.
# - Could include format type, compression, etc.

# 7) COG_PARAMS
# - Parameters for gdal_translate to convert TIFF -> Cloud Optimized GeoTIFF (COG).
# - Could include block size, compression, overviews, etc.


