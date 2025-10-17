import subprocess
import edk_sar as es
import glob
import os
from osgeo import gdal
from edk_sar.workflows.base import helpers
import numpy as np

def generate_run_files():
    run_files_cmd = [
        "bash",
        "/workspace/workflows/interferograms/generate_run_files.sh",
    ]
    es.frameworks.isce2.run_cmd(" ".join(run_files_cmd))


def execute_run_files():
    es.frameworks.isce2.run_cmd(
        "bash /workspace/workflows/interferograms/execute_run_files.sh"
    )

def run(slc_path, base_dir):
 
    # Prepare SLC processing environment
    es.workflows.base.create_netrc()
    es.workflows.base.create_folders()
    es.workflows.base.copy_slcs(slc_path)
    es.workflows.base.get_aux_file()

    # Get bounding box of SLCs and download DEM
    slcs = glob.glob(os.path.join(slc_path, "*.zip"))
    common_bbox = helpers.get_common_bbox(slcs)
    es.workflows.base.download_dem(common_bbox)

    generate_run_files()
    execute_run_files()
