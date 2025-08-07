import edk_sar as es
from osgeo import gdal
import math
import os
import logging
import xml.etree.ElementTree as ET
import glob

logger = logging.getLogger(__name__)


def generate_run_files():
    run_files_cmd = [
        "bash",
        "/workspace/workflows/coregister/generate_run_files.sh",
    ]
    es.frameworks.isce2.run_cmd(" ".join(run_files_cmd))


def execute_run_files():
    es.frameworks.isce2.run_cmd(
        "bash /workspace/workflows/coregister/execute_run_files.sh"
    )


def run(slc_path):
    es.workflows.base.create_netrc()

    # Creating folders in docker container
    es.workflows.base.create_folders()

    # Copy SLCs to docker container
    es.workflows.base.copy_slcs(slc_path)

    # Get aux file
    es.workflows.base.get_aux_file()

    slcs = glob.glob(os.path.join(slc_path, "*.zip"))
    # Getting common bounding box for all SLCs
    common_bbox = es.workflows.base.get_common_bbox(slcs)
    # Download DEM
    es.workflows.base.download_dem(common_bbox)

    # Generate run_files for coregistration
    generate_run_files()

    # Executing run files one by one
    execute_run_files()
