import argparse

import asf_search
import hyp3_sdk


HYP3_URL = 'https://hyp3-lavas.asf.alaska.edu'


def bbox_to_wkt(min_lon: float, min_lat: float, max_lon: float, max_lat: float) -> str:
    return f'POLYGON(({min_lon} {min_lat},{max_lon} {min_lat},{max_lon} {max_lat},{min_lon} {max_lat},{min_lon} {min_lat}))'


def get_granules(
    path: int, start: str, end: str, min_lon: float, min_lat: float, max_lon: float, max_lat: float
) -> list[str]:
    granules: list[str] = []
    for polarization in (asf_search.POLARIZATION.VV, asf_search.POLARIZATION.VV_VH):
        results = asf_search.geo_search(
            platform=asf_search.PLATFORM.SENTINEL1,
            processingLevel=asf_search.PRODUCT_TYPE.RAW,
            beamMode=asf_search.BEAMMODE.IW,
            polarization=polarization,
            relativeOrbit=path,
            start=start,
            end=end,
            intersectsWith=bbox_to_wkt(min_lon, min_lat, max_lon, max_lat),
        )
        granules.extend(result.properties['sceneName'] for result in results)
    return granules


def submit_job(granules: list[str], min_lon: float, min_lat: float, max_lon: float, max_lat: float) -> hyp3_sdk.Job:
    hyp3 = hyp3_sdk.HyP3(HYP3_URL)
    prepared_job = {
        'job_type': 'SRG_TIME_SERIES',
        'job_parameters': {
            'granules': granules,
            'bounds': [min_lon, min_lat, max_lon, max_lat],
        },
    }
    return hyp3.submit_prepared_jobs(prepared_job)[0]


def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('path', type=int, help='Path/track number, 1-175')
    parser.add_argument('min_lon', type=float, help='Western longitude, -180.0 to 180.0')
    parser.add_argument('min_lat', type=float, help='Southern latitude, -90.0 to 90.0')
    parser.add_argument('max_lon', type=float, help='Eastern longitude, -180.0 to 180.0')
    parser.add_argument('max_lat', type=float, help='Northern latitude, -90.0 to 90.0')
    parser.add_argument('start', help='Start of acquisition window, YYYY-MM-DD')
    parser.add_argument('end', help='End of acquisition window, YYYY-MM-DD')

    return parser.parse_args()


def main():
    args = get_args()
    granule_names = get_granules(
        args.path, args.start, args.end, args.min_lon, args.min_lat, args.max_lon, args.max_lat
    )

    if len(granule_names) == 0:
        raise ValueError('No granules found for these search criteria')

    job = submit_job(granule_names, args.min_lon, args.min_lat, args.max_lon, args.max_lat)

    print(f'\nJob {job.job_id} submitted for {len(granule_names)} granules')

    print(f'\n{HYP3_URL}/jobs/{job.job_id}')
    print('\nimport hyp3_sdk')
    print(f"hyp3 = hyp3_sdk.HyP3('{HYP3_URL}')")
    print(f"job = hyp3.get_job_by_id('{job.job_id}')")


if __name__ == '__main__':
    main()
