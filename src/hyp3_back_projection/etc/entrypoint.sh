#!/bin/bash --login
set -e
conda activate hyp3-back-projection
exec python -um hyp3_back_projection "$@"
