import edk_sar.workflows.interferograms.runner as runner

def run(slc_path, polarization=None, swath_num=None):
    runner.run(slc_path, polarization=polarization, swath_num=swath_num)