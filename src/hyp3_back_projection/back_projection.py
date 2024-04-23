"""
back-projection processing
"""

import argparse
import logging
from pathlib import Path
from typing import Optional

from hyp3_back_projection import utils


log = logging.getLogger(__name__)


def back_project(
    granule: str,
    earthdata_username: str = None,
    earthdata_password: str = None,
    esa_username: str = None,
    esa_password: str = None,
    bucket: str = None,
    bucket_prefix: str = '',
    work_dir: Optional[Path] = None,
) -> Path:
    """Back-project a Sentinel-1 level-0 granule.

    Args:
        granule: Sentinel-1 level-0 granule to back-project
        earthdata_username: Username for NASA's EarthData service
        earthdata_password: Password for NASA's EarthData service
        esa_username: Username for ESA's Copernicus Data Space Ecosystem
        esa_password: Password for ESA's Copernicus Data Space Ecosystem
        bucket: AWS S3 bucket for uploading the final product(s)
        bucket_prefix: Add a bucket prefix to the product(s)
        work_dir: Working directory for processing
    """
    if work_dir is None:
        work_dir = Path.cwd()

    granule_path = utils.download_granule(granule, work_dir)
    orbit_path = utils.download_orbit(granule, work_dir)
    # Download DEM
    # call sentinel_scene_cup.py via subprocess
    product_file = None
    return product_file


def main():
    """Back Projection entrypoint.

    Example command:
        python -m ++process back_projection S1A_IW_RAW__0SDV_20240417T132540_20240417T132613_053474_067D0B_EA25
    """
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--earthdata-username', default=None, help="Username for NASA's EarthData")
    parser.add_argument('--earthdata-password', default=None, help="Password for NASA's EarthData")
    parser.add_argument('--esa-username', default=None, help="Username for ESA's Copernicus Data Space Ecosystem")
    parser.add_argument('--esa-password', default=None, help="Password for ESA's Copernicus Data Space Ecosystem")
    parser.add_argument('--bucket', help='AWS S3 bucket HyP3 for upload the final product(s)')
    parser.add_argument('--bucket-prefix', default='', help='Add a bucket prefix to product(s)')
    # TODO: will eventually need to add to support multiple granules
    parser.add_argument('granule', help='Level-0 S1 granule to back-project.')
    args = parser.parse_args()

    back_project(**args.__dict__)


if __name__ == '__main__':
    main()
