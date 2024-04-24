"""Prepare a Copernicus GLO-30 DEM virtual raster (VRT) covering a given geometry"""
from pathlib import Path
from typing import Union, Tuple

from dem_stitcher import stitch_dem
from hyp3_back_projection import utils
from osgeo import gdal

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


def write_demfile(bounds, granule_path, dem_file: Union[str, Path]):
    dem_urls = stitch_dem.get_dem_tile_paths(bounds, granule_path.name)
    with dem_file.open('w') as f:
        [f.write(f'{dem_url.split['/'][:-1]}\n') for dem_url in dem_urls]
    return


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

    write_demfile(extent, granule_path, dem_path)
    utils.call_stanford_module(dem_script)
    return
