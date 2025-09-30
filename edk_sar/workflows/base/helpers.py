# helper functions for coregistration/interferograms workflows

# Things like geocode() function. 
# geocode() will be used to geocode different outputs of interferograms or coregistration
# It will take .vrt, lon.rdr, lat.rdr and output path as input. 
# It will add the GEOLOCATION metadata and save it as a new output file
# It will also check if lon.rdr, lat.rdr and input vrt have same dimensions, if not it should raise an error

# convert_to_cog() will be used to convert .vrt to .cog
# It will take .vrt and output path as input. 
# It will convert .vrt to .cog and save it as a new output file

import os
import subprocess
from osgeo import gdal
from lxml import etree

from edk_sar.workflows.base.bbox import get_bbox, get_common_bbox_from_boxes

def get_common_bbox(slc_paths):
    # Get bounding box for all SLCs
    bboxes = []
    for slc_path in slc_paths:
        bbox = get_bbox(slc_path)
        bboxes.append(bbox)

    common_bbox = get_common_bbox_from_boxes(bboxes)

    return common_bbox

def geocode(input_vrt: str, lon_rdr: str, lat_rdr: str, output_vrt: str):

    # Check input files
    for f in [input_vrt, lon_rdr, lat_rdr]:
        if not os.path.exists(f):
            raise FileNotFoundError(f"File not found: {f}")

    # Step 1: Add GEOLOCATION metadata
    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(input_vrt, parser)
    root = tree.getroot()

    # Remove existing GEOLOCATION metadata if present
    for md in root.xpath("//Metadata[@domain='GEOLOCATION']"):
        root.remove(md)

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

    # Append to root
    root.append(geoloc)

    # Temporary VRT with GEOLOCATION metadata
    temp_vrt = output_vrt.replace(".vrt", "_temp.vrt")
    tree.write(temp_vrt, pretty_print=True)
    print(f"[OK] GEOLOCATION metadata added: {temp_vrt}")

    # Step 2: Geocode using gdalwarp
    cmd = [
        "gdalwarp",
        "-geoloc",
        "-t_srs", "EPSG:4326",
        "-of", "VRT",
        "-srcnodata", "0",
        temp_vrt,
        output_vrt
    ]
    subprocess.run(cmd, check=True)

    # Clean up temporary file
    os.remove(temp_vrt)

    print(f"[OK] Geocoded VRT created: {output_vrt}")



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
