export ISCE_STACK=/tmp/repos/isce2/contrib/stack
export PYTHONPATH=${PYTHONPATH}:${ISCE_STACK}


# For TOPS
export PATH=${PATH}:${ISCE_STACK}/topsStack

cd /data/stack

bash /data/stack/run_files/run_01_unpack_topo_reference
bash /data/stack/run_files/run_02_unpack_secondary_slc
bash /data/stack/run_files/run_03_average_baseline
bash /data/stack/run_files/run_04_extract_burst_overlaps
bash /data/stack/run_files/run_05_overlap_geo2rdr
bash /data/stack/run_files/run_06_overlap_resample
bash /data/stack/run_files/run_07_pairs_misreg
bash /data/stack/run_files/run_08_timeseries_misreg
bash /data/stack/run_files/run_09_fullBurst_geo2rdr
bash /data/stack/run_files/run_10_fullBurst_resample
bash /data/stack/run_files/run_11_extract_stack_valid_region
bash /data/stack/run_files/run_12_merge_reference_secondary_slc
bash /data/stack/run_files/run_13_generate_burst_igram
bash /data/stack/run_files/run_14_merge_burst_igram
bash /data/stack/run_files/run_15_filter_coherence
bash /data/stack/run_files/run_16_unwrap