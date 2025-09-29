# This file contains functions common for interferograms and coregistration workflows. 
# Note this doesn't contain any helper functions like geocoding
import math
import edk_sar as es
import os
from edk_sar.workflows.base.bbox import get_bbox, get_common_bbox_from_boxes

def download_dem(bbox):
    dem_args = [
        "bash",
        "/workspace/workflows/base/get_dem.sh",
        str(math.floor(bbox[1] - 0.25)),
        str(math.ceil(bbox[3] + 0.25)),
        str(math.floor(bbox[0] - 0.25)),
        str(math.ceil(bbox[2] + 0.25)),
    ]

    dem_cmd = " ".join(dem_args)
    es.frameworks.isce2.run_cmd(dem_cmd)


def create_folders():
    es.frameworks.isce2.run_cmd("mkdir -p /data/slcs")
    es.frameworks.isce2.run_cmd("mkdir -p /data/dem")
    es.frameworks.isce2.run_cmd("mkdir -p /data/orbits")
    es.frameworks.isce2.run_cmd("mkdir -p /data/aux_cal")
    es.frameworks.isce2.run_cmd("mkdir -p /data/stack")


def copy_slcs(slc_path):
    # Copy and move files to edk_sar/data/slcs/ using cp
    dest_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../data/slcs/")
    )
    os.makedirs(dest_dir, exist_ok=True)

    os.system(f"cp -r {os.path.join(slc_path, '*.zip')} {dest_dir}/")


def get_common_bbox(slc_paths):
    # TODO: Move to helpers.py
    # Get bounding box for all SLCs
    bboxes = []
    for slc_path in slc_paths:
        bbox = get_bbox(slc_path)
        bboxes.append(bbox)

    common_bbox = get_common_bbox_from_boxes(bboxes)

    return common_bbox

def get_aux_file():
    es.frameworks.isce2.run_cmd("bash /workspace/workflows/base/get_aux_file.sh")


def create_netrc():
    es.frameworks.isce2.run_cmd("bash /workspace/workflows/base/create_netrc.sh")
