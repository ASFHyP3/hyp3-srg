"""
back-projection processing
"""

import argparse
import logging
import zipfile
from pathlib import Path
from typing import Iterable, Optional

from hyp3lib.aws import upload_file_to_s3
from shapely import unary_union

from hyp3_back_projection import dem, utils


log = logging.getLogger(__name__)


def create_param_file(dem_path: Path, dem_rsc_path: Path, output_dir: Path):
    """Create a parameter file for the processor.

    Args:
        dem_path: Path to the DEM file
        dem_rsc_path: Path to the DEM RSC file
        output_dir: Directory to save the parameter file in
    """
    lines = [str(dem_path), str(dem_rsc_path)]
    with open(output_dir / 'params', 'w') as f:
        f.write('\n'.join(lines))


def check_required_files(required_files: Iterable, work_dir: Path) -> None:
    for file in required_files:
        if not (work_dir / file).exists():
            raise FileNotFoundError(f'Missing required file: {file}')


def clean_up_after_back_projection(work_dir: Path) -> None:
    patterns = ['*hgt*', 'dem*', 'DEM*', 'q*', '*positionburst*']
    for pattern in patterns:
        [f.unlink() for f in work_dir.glob(pattern)]


def back_project_cpu(granule_orbit_pairs: Iterable, work_dir: Path) -> None:
    """Back-project a set of Sentinel-1 level-0 granules using the CPU-based workflow.

    Args:
        granule_orbit_pairs: List of tuples of granule and orbit file paths
        work_dir: Working directory for processing
    """
    check_required_files(['elevation.dem', 'elevation.dem.rsc', 'params'], work_dir)

    for granule_path, orbit_path in granule_orbit_pairs:
        args = [str(granule_path.with_suffix('')), str(orbit_path)]
        utils.call_stanford_module('sentinel/sentinel_scene_cpu.py', args, work_dir=work_dir)

    clean_up_after_back_projection(work_dir)


def create_zipped_safe_list(granule_paths: Iterable, work_dir: Path):
    """Create a list of the zipped granules to process."""
    with open(work_dir / 'ziplist', 'w') as f:
        for granule_path in granule_paths:
            f.write(f'{granule_path.name}\n')


def back_project_gpu(granule_orbit_pairs: Iterable, work_dir: Path) -> None:
    """Back-project a set of Sentinel-1 level-0 granules using the GPU-based workflow.

    Args:
        granule_orbit_pairs: List of tuples of granule and orbit file paths
        work_dir: Working directory for processing
    """
    n_gpus = utils.how_many_gpus()
    create_zipped_safe_list([x[0] for x in granule_orbit_pairs], work_dir=work_dir)

    check_required_files(['elevation.dem', 'elevation.dem.rsc', 'params', 'ziplist'])

    utils.call_stanford_module('sentinel/process_parallel.py', ['ziplist', str(n_gpus)], work_dir=work_dir)

    clean_up_after_back_projection(work_dir)


def create_product(work_dir) -> Path:
    """Create a product zip file.
    Includes files needed for further processing (gslc, orbit, and parameter file).

    Args:
        work_dir: Working directory for completed back-projection run

    Returns:
        Path to the created zip file
    """
    gslc_path = list(work_dir.glob('S1*.geo'))[0]
    product_name = gslc_path.with_suffix('').name
    orbit_path = work_dir / f'{product_name}.orbtiming'
    zip_path = work_dir / f'{product_name}.zip'

    parameter_file = work_dir / f'{product_name}.txt'
    input_granules = [x.with_suffix('').name for x in work_dir.glob('S1*.SAFE')]
    with open(parameter_file, 'w') as f:
        f.write('Process: back-projection\n')
        f.write(f"Input Granules: {', '.join(input_granules)}\n")

    # We don't compress the data because SLC data is psuedo-random
    with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_STORED) as z:
        z.write(gslc_path, gslc_path.name)
        z.write(orbit_path, orbit_path.name)
        z.write(parameter_file, parameter_file.name)

    return zip_path


def back_project(
    granules: Iterable[str],
    earthdata_username: str = None,
    earthdata_password: str = None,
    esa_username: str = None,
    esa_password: str = None,
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
        esa_username: Username for ESA's Copernicus Data Space Ecosystem
        esa_password: Password for ESA's Copernicus Data Space Ecosystem
        bucket: AWS S3 bucket for uploading the final product(s)
        bucket_prefix: Add a bucket prefix to the product(s)
        work_dir: Working directory for processing
        gpu: Use the GPU-based version of the workflow
    """
    utils.set_creds('EARTHDATA', earthdata_username, earthdata_password)
    utils.set_creds('ESA', esa_username, esa_password)
    if work_dir is None:
        work_dir = Path.cwd()

    print('Downloading data...')
    bboxs = []
    granule_orbit_pairs = []
    for granule in granules:
        unzip = True if not gpu else False
        granule_path, granule_bbox = utils.download_raw_granule(granule, work_dir, unzip)
        orbit_path = utils.download_orbit(granule, work_dir)
        bboxs.append(granule_bbox)
        granule_orbit_pairs.append((granule_path, orbit_path))

    full_bbox = unary_union(bboxs).buffer(0.1)
    dem_path = dem.download_dem_for_back_projection(full_bbox, work_dir)
    create_param_file(dem_path, dem_path.with_suffix('.dem.rsc'), work_dir)

    if gpu:
        back_project_gpu(granule_orbit_pairs, work_dir=work_dir)
    else:
        back_project_cpu(granule_orbit_pairs, work_dir=work_dir)

    utils.call_stanford_module('util/merge_slcs.py', work_dir=work_dir)

    if bucket:
        zip_path = create_product(work_dir)
        upload_file_to_s3(zip_path, bucket, bucket_prefix)

    print(f'Finished back-projection for {list(work_dir.glob("S1*.geo"))[0].with_suffix("").name}!')


def main():
    """Back Projection entrypoint.

    Example command:
    python -m hyp3_back_projection ++process back_projection \
        S1A_IW_RAW__0SDV_20231229T134339_20231229T134411_051870_064437_4F42-RAW \
        S1A_IW_RAW__0SDV_20231229T134404_20231229T134436_051870_064437_5F38-RAW
    """
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--earthdata-username', default=None, help="Username for NASA's EarthData")
    parser.add_argument('--earthdata-password', default=None, help="Password for NASA's EarthData")
    parser.add_argument('--esa-username', default=None, help="Username for ESA's Copernicus Data Space Ecosystem")
    parser.add_argument('--esa-password', default=None, help="Password for ESA's Copernicus Data Space Ecosystem")
    parser.add_argument('--bucket', help='AWS S3 bucket HyP3 for upload the final product(s)')
    parser.add_argument('--bucket-prefix', default='', help='Add a bucket prefix to product(s)')
    parser.add_argument('--gpu', default=False, action='store_true', help='Use the GPU-based version of the workflow.')
    parser.add_argument('granules', nargs='+', help='Level-0 S1 granule to back-project.')
    args = parser.parse_args()

    back_project(**args.__dict__)


if __name__ == '__main__':
    main()
