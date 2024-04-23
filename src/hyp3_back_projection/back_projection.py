"""
back-projection processing
"""

import argparse
import logging
from pathlib import Path

from hyp3_back_projection import utils


log = logging.getLogger(__name__)


def back_project(granule) -> Path:
    """Back-project a Sentinel-1 level-0 granule.

    Args:
        granule: Sentinel-1 level-0 granule to back-project
    """
    utils.download_granule(granule)
    # Download orbit file
    # Download DEM
    # call sentinel_scene_cup.py via subprocess
    product_file = None
    return product_file


def main():
    """process_back_projection entrypoint"""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--bucket', help='AWS S3 bucket HyP3 for upload the final product(s)')
    parser.add_argument('--bucket-prefix', default='', help='Add a bucket prefix to product(s)')
    parser.add_argument('--esa-username', default=None, help="Username for ESA's Copernicus Data Space Ecosystem")
    parser.add_argument('--esa-password', default=None, help="Password for ESA's Copernicus Data Space Ecosystem")
    parser.add_argument('--earthdata-username', default=None, help="Username for NASA's EarthData")
    parser.add_argument('--earthdata-password', default=None, help="Password for NASA's EarthData")
    # TODO: will eventually need to add to support multiple granules
    parser.add_argument('granule', nargs=1, help='Level-0 S1 granule to back-project.')
    args = parser.parse_args()

    back_project(**args.__dict__)


if __name__ == '__main__':
    main()
