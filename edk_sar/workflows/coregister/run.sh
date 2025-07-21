# Setting TOPS Stack
export ISCE_STACK=/tmp/repos/isce2/contrib/stack
export PYTHONPATH=${PYTHONPATH}:${ISCE_STACK}


# For TOPS
export PATH=${PATH}:${ISCE_STACK}/topsStack

# Running stackSentinel.py -h
/tmp/repos/isce2/contrib/stack/topsStack/stackSentinel.py -h