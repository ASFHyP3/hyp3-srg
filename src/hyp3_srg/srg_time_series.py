"""
GSLC SRG Time-series processing
"""

import argparse
import logging
import os
import zipfile
from pathlib import Path
from typing import Iterable, Optional

from hyp3lib.aws import upload_file_to_s3
from shapely import unary_union

from hyp3_srg import dem, utils


def srg_time_series(
    granules: Iterable[str],
    earthdata_username: str = None,
    earthdata_password: str = None,
    bucket: str = None,
    bucket_prefix: str = '',
    work_dir: Optional[Path] = None,
    gpu: bool = False,
):
    """Back-project a set of Sentinel-1 level-0 granules.

    Args:
        granules: List of Sentinel-1 level-0 granules to back-project
        earthdata_username: Username for NASA's EarthData service
        earthdata_password: Password for NASA's EarthData service
        bucket: AWS S3 bucket for uploading the final product(s)
        bucket_prefix: Add a bucket prefix to the product(s)
        work_dir: Working directory for processing
        gpu: Use the GPU-based version of the workflow
    """
    utils.set_creds('EARTHDATA', earthdata_username, earthdata_password)
    if work_dir is None:
        work_dir = Path.cwd()

    print('Downloading data...')
    bboxs = []
    granule_orbit_pairs = []
    for granule in granules:
        granule_path, granule_bbox = utils.download_raw_granule(granule, work_dir, unzip=True)
        orbit_path = utils.download_orbit(granule, work_dir)
        bboxs.append(granule_bbox)
        granule_orbit_pairs.append((granule_path, orbit_path))

    full_bbox = unary_union(bboxs).buffer(0.1)
    dem_path = dem.download_dem_for_srg(full_bbox, work_dir)
    create_param_file(dem_path, dem_path.with_suffix('.dem.rsc'), work_dir)

    #TIME SERIES ANLAYSIS
    utils.call_stanford_module('util/merge_slcs.py', work_dir=work_dir)

    zip_path = create_product(work_dir)
    if bucket:
        upload_file_to_s3(zip_path, bucket, bucket_prefix)

    print(f'Finished SRG time series for {list(work_dir.glob("S1*.geo"))[0].with_suffix("").name}!')


def main():
    """Back Projection entrypoint.

    Example command:
    python -m hyp3_srg ++process back_projection \
        S1A_IW_RAW__0SDV_20231229T134339_20231229T134411_051870_064437_4F42-RAW \
        S1A_IW_RAW__0SDV_20231229T134404_20231229T134436_051870_064437_5F38-RAW
    """
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--earthdata-username', default=None, help="Username for NASA's EarthData")
    parser.add_argument('--earthdata-password', default=None, help="Password for NASA's EarthData")
    parser.add_argument('--bucket', help='AWS S3 bucket HyP3 for upload the final product(s)')
    parser.add_argument('--bucket-prefix', default='', help='Add a bucket prefix to product(s)')
    parser.add_argument('--gpu', default=False, action='store_true', help='Use the GPU-based version of the workflow.')
    parser.add_argument('granules', type=str.split, nargs='+', help='')
    args = parser.parse_args()
    args.granules = [item for sublist in args.granules for item in sublist]
    srg_time_series(**args.__dict__)


if __name__ == '__main__':
    main()