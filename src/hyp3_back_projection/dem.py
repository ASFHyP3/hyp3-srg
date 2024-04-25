"""Prepare a Copernicus GLO-30 DEM virtual raster (VRT) covering a given geometry"""
import logging
from pathlib import Path

import boto3
from shapely.geometry import Polygon

from hyp3_back_projection import utils


log = logging.getLogger(__name__)


def ensure_egm_model_available():
    """Ensure the EGM module is available.
    Currently using the EGM2004 model provided by Stanford, but hope to switch to a public source.
    """
    proc_home = utils.get_proc_home()
    egm_model_path = proc_home / 'DEM' / 'egm2008_geoid_grid'
    if not egm_model_path.exists():
        print('EGM2008 model not found. Downloading from S3.')
        s3 = boto3.client('s3')
        s3.download_file('ffwilliams2-shenanigans', 'lavas/egm2008_geoid_grid', egm_model_path)


def download_dem_for_back_projection(
    footprint: Polygon,
    output_dir: Path,
) -> Path:
    """Download the given DEM for the given extent.

    Args:
        footprint: The footprint to download a DEM for.

    Returns:
        The path to the downloaded DEM.
    """
    dem_path = output_dir / 'elevation.dem'
    dem_rsc = output_dir / 'elevation.dem.rsc'

    ensure_egm_model_available()

    # bounds produces min x, min y, max x, max y; stanford wants toplat, botlat, leftlon, rightlon
    stanford_bounds = [footprint.bounds[i] for i in [3, 1, 0, 2]]
    args = [dem_path, dem_rsc, *stanford_bounds]
    utils.call_stanford_module('DEM/createDEMcop.py', args)
    return dem_path
