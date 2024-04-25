"""Prepare a Copernicus GLO-30 DEM virtual raster (VRT) covering a given geometry"""
from pathlib import Path

from shapely.geometry import Polygon

from hyp3_back_projection import utils

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

    stanford_bounds = [footprint.bounds[i] for i in [3, 2, 0, 1]]
    args = [dem_path, dem_rsc, *stanford_bounds]
    utils.call_stanford_module('DEM/createDEMcop.py', args)
    return dem_path
