#!/bin/bash

# Usage: dem.sh <W> <S> <E> <N> <output_dir>
# Example: ./dem.sh -123.5 45.0 -122.0 46.0 /path/to/output-dir
S=$1
N=$2
W=$3
E=$4
OUTDIR=$5

USERNAME=$6
PASSWORD=$7
URL=$8

mkdir -p $OUTDIR
cd $OUTDIR

/usr/lib/python3.8/dist-packages/isce2/applications/dem.py -a stitch -b $S $N $W $E -r -s 1 -c --dir $OUTDIR -n $USERNAME -w $PASSWORD -u $URL