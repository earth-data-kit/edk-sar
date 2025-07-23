import edk_sar as es
from osgeo import gdal
import math
import os
import logging
import xml.etree.ElementTree as ET
from edk_sar.workflows.coregister.bbox import get_bbox, get_common_bbox
import glob

logger = logging.getLogger(__name__)


def _download_dem(bbox):
    dem_args = [
        "bash",
        "/workspace/workflows/coregister/get_dem.sh",
        str(math.floor(bbox[1] - 0.25)),
        str(math.ceil(bbox[3] + 0.25)),
        str(math.floor(bbox[0] - 0.25)),
        str(math.ceil(bbox[2] + 0.25)),
    ]

    dem_cmd = " ".join(dem_args)
    es.frameworks.isce2.run_cmd(dem_cmd)


def _create_folders():
    es.frameworks.isce2.run_cmd("mkdir -p /data/slcs")
    es.frameworks.isce2.run_cmd("mkdir -p /data/dem")
    es.frameworks.isce2.run_cmd("mkdir -p /data/orbits")
    es.frameworks.isce2.run_cmd("mkdir -p /data/aux_cal")
    es.frameworks.isce2.run_cmd("mkdir -p /data/stack")


def _copy_slcs(slc_path):
    # Copy and move files to edk_sar/data/slcs/ using cp
    dest_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../data/slcs/")
    )
    os.makedirs(dest_dir, exist_ok=True)

    os.system(f"cp -r {os.path.join(slc_path, '*.zip')} {dest_dir}/")


def _generate_run_files():
    run_files_cmd = [
        "bash",
        "/workspace/workflows/coregister/generate_run_files.sh",
    ]
    es.frameworks.isce2.run_cmd(" ".join(run_files_cmd))


def _get_common_bbox(slc_paths):
    # Get bounding box for all SLCs
    bboxes = []
    for slc_path in slc_paths:
        bbox = get_bbox(slc_path)
        bboxes.append(bbox)

    common_bbox = get_common_bbox(bboxes)

    return common_bbox


def _execute_run_files():
    es.frameworks.isce2.run_cmd(
        "bash /workspace/workflows/coregister/execute_run_files.sh"
    )


def _get_aux_file():
    es.frameworks.isce2.run_cmd("bash /workspace/workflows/coregister/get_aux_file.sh")


def _create_netrc():
    es.frameworks.isce2.run_cmd("bash /workspace/workflows/coregister/create_netrc.sh")


def _run(slc_path):
    slcs = glob.glob(os.path.join(slc_path, "*.zip"))

    _create_netrc()

    # Creating folders in docker container
    _create_folders()

    # Getting common bounding box for all SLCs
    common_bbox = _get_common_bbox(slcs)

    # Download DEM
    _download_dem(common_bbox)

    # Copy SLCs to docker container
    _copy_slcs(slc_path)

    # Get aux file
    _get_aux_file()

    # Generate run_files for coregistration
    _generate_run_files()

    # Executing run files one by one
    _execute_run_files()
