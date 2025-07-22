import edk_sar as es
from osgeo import gdal
import math
import os
import logging
import xml.etree.ElementTree as ET
from edk_sar.workflows.coregister.bbox import get_bbox, get_common_bbox

logger = logging.getLogger(__name__)

def _run(slc_paths):
    # Get bounding box for all SLCs
    bboxes = []
    for slc_path in slc_paths:
        bbox = get_bbox(slc_path)
        bboxes.append(bbox)

    common_bbox = get_common_bbox(bboxes)

    # Download DEM
    dem_args = [
        "bash",
        '/workspace/workflows/coregister/dem.sh',
        str(math.floor(common_bbox[1] - 0.25)),
        str(math.ceil(common_bbox[3] + 0.25)),
        str(math.floor(common_bbox[0] - 0.25)),
        str(math.ceil(common_bbox[2] + 0.25)),
        '/data/dem',
        os.environ.get("DEM_USERNAME"),
        os.environ.get("DEM_PASSWORD"),
        es.constants.DEM_URL
    ]
    dem_cmd = " ".join(dem_args)
    es.frameworks.isce2.run_cmd(dem_cmd)

    # Generate run_files for coregistration

    # Execute all run_files one by one
    return
    # logger.info(f"Running DEM download script: {' '.join(dem_args)}")
    # subprocess.run(dem_args, check=True)
    return
    # 4. Run the coregistration command to generate run_files
    # Example: stackSentinel.py -s <slc_paths> -d <dem_dir> -W slc --num_proc 2 --num_proc4topo 2 -w <work_dir>
    stack_script = "/home/ubuntu/sar/isce2/contrib/stack/topsStack/stackSentinel.py"
    slc_arg = ",".join(slc_paths)
    run_cmd = [
        stack_script,
        "-s", slc_arg,
        "-d", dem_dir,
        "-W", "slc",
        "--num_proc", "2",
        "--num_proc4topo", "2",
        "-w", work_dir
    ]
    logger.info(f"Running coregistration command: {' '.join(run_cmd)}")
    subprocess.run(run_cmd, check=True)

    # 5. Execute all run files one by one
    run_files_dir = os.path.join(work_dir, "run_files")
    if not os.path.exists(run_files_dir):
        logger.error(f"Run files directory does not exist: {run_files_dir}")
        return

    run_files = [os.path.join(run_files_dir, f) for f in os.listdir(run_files_dir) if f.endswith(".sh")]
    run_files.sort()
    for run_file in run_files:
        logger.info(f"Executing run file: {run_file}")
        subprocess.run(["bash", run_file], check=True)