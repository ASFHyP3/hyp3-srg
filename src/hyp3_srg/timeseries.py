"""
Sentinel-1 GSLC timeseries interferogram processing
"""

import argparse
import logging
from pathlib import Path
from typing import Iterable, Optional

from shapely import unary_union

from hyp3_srg import dem, utils

log = logging.getLogger(__name__)


def timeseries(
    granules: Iterable[str],
    bucket: str = None,
    bucket_prefix: str = '',
    work_dir: Optional[Path] = None,
):
    """Create a timeseries interferogram from a set of Sentinel-1 GSLCs.

    Args:
        granules: List of Sentinel-1 GSLCs
        bucket: AWS S3 bucket for uploading the final product(s)
        bucket_prefix: Add a bucket prefix to the product(s)
        work_dir: Working directory for processing
    """
    if work_dir is None:
        work_dir = Path.cwd()

    bboxs = []
    for granule in granules:
        bboxs.append(utils.get_bbox(granule))

    full_bbox = unary_union(bboxs).buffer(0.1)
    dem_path = dem.download_dem_for_srg(full_bbox, work_dir)
    utils.create_param_file(dem_path, dem_path.with_suffix('.dem.rsc'), work_dir)

    pass


def main():
    """Timeseries entrypoint.

    Example command:
    python -m hyp3_srg ++process timeseries \
        S1A_IW_RAW__0SDV_20231229T134339_20231229T134411_051870_064437_4F42 \
        S1A_IW_RAW__0SDV_20231229T134404_20231229T134436_051870_064437_5F38
    """
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--bucket', help='AWS S3 bucket HyP3 for upload the final product(s)')
    parser.add_argument('--bucket-prefix', default='', help='Add a bucket prefix to product(s)')
    parser.add_argument('granules', type=str.split, nargs='+', help='GSLC granules.')
    args = parser.parse_args()
    args.granules = [item for sublist in args.granules for item in sublist]
    timeseries(**args.__dict__)


if __name__ == '__main__':
    main()
