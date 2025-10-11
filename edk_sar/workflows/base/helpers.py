import os
import subprocess
from osgeo import gdal,osr
from lxml import etree
from shapely.geometry import Polygon, box
import zipfile
import logging

logger = logging.getLogger(__name__)

def get_bbox_from_gcps(raster_path):
    ds = gdal.Open(raster_path)
    gcps = ds.GetGCPs()
    if not gcps:
        raise ValueError("No GCPs found")

    # Get GCP projection
    srs = osr.SpatialReference()
    srs.ImportFromWkt(ds.GetGCPProjection())
    tgt_srs = osr.SpatialReference()
    tgt_srs.ImportFromEPSG(4326)  # WGS 84

    transform = osr.CoordinateTransformation(srs, tgt_srs)

    # Convert all GCPs to lat/lon
    points = [] 
    for gcp in gcps:
        x, y, _ = transform.TransformPoint(gcp.GCPX, gcp.GCPY)
        points.append((x, y))  # (lon, lat)

    polygon = Polygon(points)
    return polygon.bounds  # (min_lon, min_lat, max_lon, max_lat)

def get_measurement_file_paths(safe_fp):
    # Get all file paths inside the 'measurement' directory within the zip, without extracting
    measurement_file_paths = []
    with zipfile.ZipFile(safe_fp, "r") as zf:
        # Find the .SAFE root directory in the zip
        safe_dirs = set()
        for name in zf.namelist():
            if name.endswith(".SAFE/"):
                safe_dirs.add(name)
        if not safe_dirs:
            # Try to infer .SAFE root from file paths
            for name in zf.namelist():
                if ".SAFE/" in name:
                    safe_dirs.add(name.split(".SAFE/")[0] + ".SAFE/")
        if not safe_dirs:
            logger.warning(f"No .SAFE directory found in {safe_fp}")
        else:
            safe_dir = sorted(safe_dirs)[0]
            measurement_prefix = safe_dir + "measurement/"
            for name in zf.namelist():
                if name.startswith(measurement_prefix) and not name.endswith("/"):
                    measurement_file_paths.append(name)
    return measurement_file_paths

def get_bbox(slc_path):
    measurement_file_paths = get_measurement_file_paths(slc_path)

    bboxes = []
    for mfp in measurement_file_paths:
        bbox = get_bbox_from_gcps(f"/vsizip/{slc_path}/{mfp}")
        bboxes.append(bbox)

    if not bboxes:
        return None
    min_lon = min(b[0] for b in bboxes)
    min_lat = min(b[1] for b in bboxes)
    max_lon = max(b[2] for b in bboxes)
    max_lat = max(b[3] for b in bboxes)

    return (min_lon, min_lat, max_lon, max_lat)

def get_common_bbox_from_boxes(bboxes):
    if not bboxes or any(b is None for b in bboxes):
        logger.error("Could not compute bounding boxes.")
        return

    # Convert each bbox (min_lon, min_lat, max_lon, max_lat) to a shapely box
    polygons = [box(*b) for b in bboxes]
    intersection = polygons[0]
    for poly in polygons[1:]:
        intersection = intersection.intersection(poly)
        if intersection.is_empty:
            raise ValueError("No common bounding box.")

    return intersection.bounds  # (min_lon, min_lat, max_lon, max_lat)

def get_common_bbox(slc_paths):
    # Get bounding box for all SLCs
    bboxes = []
    for slc_path in slc_paths:
        bbox = get_bbox(slc_path)
        bboxes.append(bbox)

    common_bbox = get_common_bbox_from_boxes(bboxes)

    return common_bbox


def geocode(input_vrt: str, lon_rdr: str, lat_rdr: str, output_vrt: str):
    """
    Geocode a VRT using given longitude and latitude reference rasters.

    Raises an error if:
      - Input files do not exist
      - Raster sizes do not match
      - GEOLOCATION metadata already exists
    """

    # Check input files exist
    for f in [input_vrt, lon_rdr, lat_rdr]:
        if not os.path.exists(f):
            raise FileNotFoundError(f"File not found: {f}")

    # Check raster sizes
    ds_input = gdal.Open(input_vrt)
    ds_lon = gdal.Open(lon_rdr)
    ds_lat = gdal.Open(lat_rdr)
    if ds_input is None or ds_lon is None or ds_lat is None:
        raise RuntimeError("Failed to open one of the input datasets.")

    input_size = (ds_input.RasterXSize, ds_input.RasterYSize)
    lon_size = (ds_lon.RasterXSize, ds_lon.RasterYSize)
    lat_size = (ds_lat.RasterXSize, ds_lat.RasterYSize)

    if input_size != lon_size or input_size != lat_size:
        raise ValueError(
            f"Raster size mismatch:\n"
            f"input_vrt: {input_size}\n"
            f"lon_rdr: {lon_size}\n"
            f"lat_rdr: {lat_size}"
        )

    # Parse VRT XML
    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(input_vrt, parser)
    root = tree.getroot()

    # Check if GEOLOCATION metadata already exists
    geoloc_nodes = root.xpath("//Metadata[@domain='GEOLOCATION']")
    if geoloc_nodes:
        raise RuntimeError(f"GEOLOCATION metadata already exists in {input_vrt}")

    # Create new GEOLOCATION metadata
    geoloc = etree.Element("Metadata", domain="GEOLOCATION")
    etree.SubElement(geoloc, "MDI", key="X_DATASET").text = lon_rdr
    etree.SubElement(geoloc, "MDI", key="X_BAND").text = "1"
    etree.SubElement(geoloc, "MDI", key="Y_DATASET").text = lat_rdr
    etree.SubElement(geoloc, "MDI", key="Y_BAND").text = "1"
    etree.SubElement(geoloc, "MDI", key="PIXEL_OFFSET").text = "0"
    etree.SubElement(geoloc, "MDI", key="LINE_OFFSET").text = "0"
    etree.SubElement(geoloc, "MDI", key="PIXEL_STEP").text = "1"
    etree.SubElement(geoloc, "MDI", key="LINE_STEP").text = "1"

    # Creating intermediate VRT with geolocation (keep same name pattern)
    base_dir = os.path.dirname(output_vrt)
    base_name = os.path.basename(output_vrt).replace(".vrt", "")
    temp_vrt = os.path.join(base_dir, f"{base_name}_with_geoloc.vrt")
    
    root.append(geoloc)
    tree.write(temp_vrt, pretty_print=True)
    print(f"[OK] GEOLOCATION metadata added: {temp_vrt}")

    # Geocode using gdalwarp
    cmd = [
        "gdalwarp",
        "-overwrite", 
        "-geoloc",
        "-t_srs", "EPSG:4326",
        "-of", "VRT",
        temp_vrt,
        output_vrt
    ]
    subprocess.run(cmd, check=True)

    # now we are not deleting temp file - the output VRT references it!
    print(f"[OK] Geocoded VRT created: {output_vrt}")
    print(f"[INFO] Keeping intermediate file: {temp_vrt}")

    return output_vrt

def convert_to_cog(input_file: str, output_file: str):
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input raster not found: {input_file}")

    cmd = [
        "gdalwarp",
        "-geoloc",
        "-t_srs", "EPSG:4326",
        "-of", "COG",
        "-co", "COMPRESS=LZW",
        "-co", "BIGTIFF=IF_SAFER",
        "-co", "OVERVIEWS=AUTO",
        input_file,
        output_file,
    ]
    #gdalwarp -geoloc -t_srs EPSG:4326 \ -of COG \ -co COMPRESS=LZW \ -co BIGTIFF=IF_SAFER \ -co OVERVIEWS=AUTO \ slc_with_geo.vrt slc_geocoded.tif

    subprocess.run(cmd, check=True)

    print(f"[OK] Geocoded + converted {input_file} -> {output_file} (COG)")
