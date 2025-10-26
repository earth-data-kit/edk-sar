import glob
import os
import logging
import edk_sar as es
from edk_sar.workflows.base import helpers

logger = logging.getLogger(__name__)

def run(slc_path, polarization=None, swath_nums=None):
    # --- 1. Prepare environment ---
    es.workflows.base.create_netrc()
    es.workflows.base.create_folders()
    es.workflows.base.copy_slcs(slc_path)
    es.workflows.base.get_aux_file()

    # --- 2. Download DEM ---
    slcs = glob.glob(os.path.join(slc_path, "*.zip"))
    common_bbox = helpers.get_common_bbox(slcs)
    es.workflows.base.download_dem(common_bbox)

    # --- 3. Generate and execute run files ---
    generate_run_files(polarization, swath_nums)
    execute_run_files()


def generate_run_files(polarization=None, swath_nums=None):
    run_files_cmd = [
        "bash",
        "/workspace/workflows/interferograms/generate_run_files.sh",
    ]

    if polarization is not None:
        run_files_cmd += ["-p", str(polarization)]
    if swath_nums is not None:
        run_files_cmd += ["-n", str(swath_nums)]

    # Convert to a safe command string
    cmd_str = " ".join(f'"{x}"' for x in run_files_cmd)
    logger.info(f"Generating run files: {cmd_str}")

    es.frameworks.isce2.run_cmd(cmd_str)


def execute_run_files():
    cmd_str = "bash /workspace/workflows/interferograms/execute_run_files.sh"
    logger.info(f"Executing run files: {cmd_str}")
    es.frameworks.isce2.run_cmd(cmd_str)
