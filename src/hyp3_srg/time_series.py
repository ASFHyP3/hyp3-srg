"""
Sentinel-1 GSLC time series processing
"""

import argparse
import logging
from shutil import copyfile
from pathlib import Path
from typing import Iterable, Optional

from shapely import unary_union

from hyp3_srg import dem, utils

log = logging.getLogger(__name__)


def get_size_from_dem(dem_file: str) -> tuple[int]:
    """ Get the length and width from a .rsc DEM file

    Args:
        dem_file: path to the .rsc dem file.

    Returns:
        dem_width, dem_length: tuple containing the dem width and dem length
    """
    with open(dem_file) as dem:
        width_line = dem.readline()
        dem_width = width_line.split()[1]
        length_line = dem.readline()
        dem_length = length_line.split()[1]

    return dem_width, dem_length


def generate_wrapped_interferograms(
    looks: tuple[int],
    baselines: tuple[int],
    dem_shape: tuple[int],
    work_dir: Path
) -> None:
    """ Generates wrapped interferograms from GSLCs

    Args:
        looks: tuple containing the number range looks and azimuth looks
        baselines: tuple containing the time baseline and spatial baseline
        dem_shape: tuple containing the dem width and dem length
        work_dir: the directory containing the GSLCs
    """
    dem_width, dem_length = dem_shape
    looks_down, looks_across = looks
    time_baseline, spatial_baseline = baselines

    utils.call_stanford_module(
        'sentinel/sbas_list.py',
        args=[time_baseline, spatial_baseline],
        work_dir=work_dir
    )

    sbas_args = [
        'sbas_list ../elevation.dem.rsc 1 1',
        dem_width,
        dem_length,
        looks_down,
        looks_across
    ]
    utils.call_stanford_module('sentinel/ps_sbas_igrams.py', args=sbas_args, work_dir=work_dir)


def unwrap_interferograms(
    dem_shape: tuple[int],
    unw_shape: tuple[int],
    work_dir: Path
) -> None:
    """ Unwraps wrapped interferograms in parallel

    Args:
        dem_shape: tuple containing the dem width and dem length
        unw_shape: tuple containing the width and length from the dem.rsc file
        work_dir: the directory containing the wrapped interferograms
    """
    dem_width, dem_length = dem_shape
    unw_width, unw_length = unw_shape

    reduce_dem_args = [
        '../elevation.dem dem',
        dem_width,
        dem_width // unw_width,
        dem_length // unw_length
    ]
    utils.call_stanford_module('util/nbymi2.py', args=reduce_dem_args, work_dir=work_dir)
    utils.call_stanford_module('util/unwrap_parallel.py', args=[unw_width], work_dir=work_dir)


def compute_sbas_velocity_solution(
    threshold: float,
    do_tropo_correction: bool,
    unw_shape: tuple[int],
    work_dir: Path
) -> None:
    """ Computes the sbas velocity solution from the unwrapped interferograms

    Args:
        threshold: ...
        do_tropo_correction: ...
        unw_shape: tuple containing the width and length from the dem.rsc file
        work_dir: the directory containing the wrapped interferograms
    """
    utils.call_stanford_module('sbas/sbas_setup.py',  args=['sbas_list geolist'], work_dir=work_dir)
    copyfile('./intlist', 'unwlist')
    utils.call_stanford_module('util/sed.py', args=["'s/int/unw/g' unwlist"], work_dir=work_dir)

    num_unw_files = 0
    num_slcs = 0
    with (open('unwlist', 'r'), open('geolist', 'r')) as (unw_list, slc_list):
        num_unw_files = len(unw_list.readlines())
        num_slcs = len(slc_list.readlines())

    ref_point_args = [
        'unwlist',
        unw_shape[0],
        unw_shape[1],
        threshold
    ]
    utils.call_stanford_module('int/findrefpoints', args=ref_point_args, work_dir=work_dir)

    if do_tropo_correction:
        tropo_correct_args = [
            'unwlist',
            unw_shape[0],
            unw_shape[1]
        ]
        utils.call_stanford_module('int/tropocorrect.py', args=tropo_correct_args, work_dir=work_dir)

    sbas_velocity_args = [
        'unwlist',
        str(num_unw_files.decode()).rstrip(),
        str(num_slcs.decode()).rstrip(),
        unw_shape[0],
        'ref_locs'
    ]
    utils.call_stanford_module('sbas/sbas', args=sbas_velocity_args, work_dir=work_dir)



def create_time_series(
    looks: tuple[int] = (10, 10),
    baselines: tuple[int] = (1000, 1000),
    threshold: float = 0.5,
    do_tropo_correction: bool = True,
    work_dir: Path | None = None
) -> None:
    """ Creates a time series from a stack of GSLCs consisting of interferograms and a velocity solution 

    Args:
        looks: tuple containing the number range looks and azimuth looks
        baselines: tuple containing the time baseline and spatial baseline
        threshold: ...
        do_tropo_correction: ...
        work_dir: the directory containing the GSLCs to do work in
    """
    dem_shape = get_size_from_dem('../elevation.dem.rsc')
    generate_wrapped_interferograms(looks=looks, baselines=baselines, dem_shape=dem_shape)

    unw_shape = get_size_from_dem('../dem.rsc')
    unwrap_interferograms(dem_shape=dem_shape, unw_shape=unw_shape)

    compute_sbas_velocity_solution(
        threshold=threshold,
        do_tropo_correction=do_tropo_correction,
        unw_shape=unw_shape,
        work_dir=work_dir
    )


def time_series(
    granules: Iterable[str],
    bucket: str = None,
    bucket_prefix: str = '',
    work_dir: Optional[Path] = None,
) -> None:
    """Create and package a time series stack from a set of Sentinel-1 GSLCs.

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

    utils.call_stanford_module('util/merge_slcs.py', work_dir=work_dir)

    create_time_series(work_dir=work_dir)


def main():
    """Entrypoint for the GSLC time series workflow.

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
    time_series(**args.__dict__)


if __name__ == '__main__':
    main()
