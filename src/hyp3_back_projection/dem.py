"""Prepare a Copernicus GLO-30 DEM virtual raster (VRT) covering a given geometry"""
import os
from pathlib import Path
from typing import Union, Tuple

from osgeo import gdal
from dem_stitcher import stitch_dem

gdal.UseExceptions()


def get_coordinates(info: dict) -> Tuple[int, int, int, int]:
    """Get the corner coordinates from a GDAL Info dictionary

    Args:
        info: The dictionary returned by a gdal.Info call

    Returns:
        (west, south, east, north): the corner coordinates values
    """
    try:
        if info['CRS'] == 'EPSG:4326':
            west, south = info['cornerCoordinates']['lowerLeft']
            east, north = info['cornerCoordinates']['upperRight']
            return west, south, east, north
    except AttributeError:
        # TODO: Add in a gdal warp or something to bring to EPSG4326
        print('Granule needs to be in EPSG')

def write_demfile(bounds, dem_file: Union[str, Path]):
    X, p = stitch_dem(bounds,
                      dem_name='glo_30',  # Global Copernicus 30 meter resolution DEM
                      dst_ellipsoidal_height=False,
                      dst_area_or_point='Point')
    p.

def download_dem_for_back_projection(
        granule_path: Union[Path, str],
        dem_dir: Path = '/home/user/back_projection/DEM',
) -> Path:
    """Download the given DEM for the given extent.

    Args:
        granule_path: path to downloaded granule
        dem_dir: path to the back_projection DEM directory
    Returns:
        The path to the downloaded DEM.
    """
    dem_path = dem_dir / 'demfiles.txt'
    dem_script = dem_dir / 'createDEMcop.py'

    granule_info = gdal.Info(granule_path, format='json')
    extent = get_coordinates(granule_info)

    write_demfile(extent, dem_path)
    exec(open(dem_script).read())
    return dem_path