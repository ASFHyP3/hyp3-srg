#!/bin/bash --login
set -e
conda activate hyp3-srg
exec python -um hyp3_srg "$@"
