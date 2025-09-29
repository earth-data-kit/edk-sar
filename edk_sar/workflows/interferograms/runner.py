import edk_sar as es
import glob
import os
import compute_phase
import compute_displacement
import convert_to_tiff
import convert_to_cog
import geocode_vrts

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


def run(slc_path):
    es.workflows.base.create_netrc()
    es.workflows.base.create_folders()
    
    es.workflows.base.copy_slcs(slc_path)

    es.workflows.base.get_aux_file()
    
    slcs = glob.glob(os.path.join(slc_path, "*.zip"))
    common_bbox = es.workflows.base.get_common_bbox(slcs)
    es.workflows.base.download_dem(common_bbox)


    generate_run_files()

    execute_run_files()

    geocode_vrts.run()         # geocodes VRTs -> _geo.vrt
    compute_phase.run()         # generates phase.vrt
    compute_displacement.run()      # generates displacement.vrt
    convert_to_tiff.run()           # converts VRTs -> GeoTIFFs
    convert_to_cog.run()        # converts GeoTIFFs -> COGs

    