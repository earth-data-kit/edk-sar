import os
import subprocess
from osgeo import gdal, osr
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
