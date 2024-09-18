"""Prepare a Copernicus GLO-30 DEM virtual raster (VRT) covering a given geometry"""
import logging
from pathlib import Path
from typing import Optional

import requests
from shapely.geometry import Polygon

from hyp3_srg import utils


log = logging.getLogger(__name__)


def ensure_egm_model_available():
    """Ensure the EGM module is available.
    Currently using the EGM2004 model provided by Stanford, but hope to switch to a public source.
    """
    url = 'https://ffwilliams2-shenanigans.s3.us-west-2.amazonaws.com/lavas/egm2008_geoid_grid'

    proc_home = utils.get_proc_home()
    egm_model_path = proc_home / 'DEM' / 'egm2008_geoid_grid'

    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(egm_model_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)


def download_dem_for_srg(
    footprint: Polygon,
    work_dir: Path,
) -> Path:
    """Download the given DEM for the given extent.

    Args:
        footprint: The footprint to download a DEM for
        work_dir: The directory to save create the DEM in

    Returns:
        The path to the downloaded DEM
    """
    dem_path = work_dir / 'elevation.dem'
    dem_rsc = work_dir / 'elevation.dem.rsc'

    ensure_egm_model_available()

    # bounds produces min x, min y, max x, max y; stanford wants toplat, botlat, leftlon, rightlon
    stanford_bounds = [footprint.bounds[i] for i in [3, 1, 0, 2]]
    args = [str(dem_path), str(dem_rsc), *stanford_bounds]
    utils.call_stanford_module('DEM/createDEMcop.py', args, work_dir=work_dir)
    return dem_path


def download_dem_from_bounds(bounds: list[float], work_dir: Optional[Path]):
    if (bounds[0] <= bounds[1] or bounds[2] >= bounds[3]):
        raise ValueError("Improper bounding box formatting, should be [max latitude, min latitude, min longitude, max longitude].")

    dem_path = work_dir / 'elevation.dem'
    dem_rsc = work_dir / 'elevation.dem.rsc'

    ensure_egm_model_available()

    args = [str(dem_path), str(dem_rsc), *bounds]
    utils.call_stanford_module('DEM/createDEMcop.py', args, work_dir=work_dir)
    return dem_path
