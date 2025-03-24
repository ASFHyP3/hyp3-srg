import argparse
import pprint

import asf_search
import hyp3_sdk


sites = {
    'etna': {
        'path': 124,
        'bbox': [14.544568, 37.388676, 15.453432, 38.107324],
        'start': '2013-01-01T00:00:00Z',
        'end': '2026-01-01T00:00:00Z',
    },
   'kilauea': {
        'path': 87,
        'bbox': [-155.668003, 19.06167553, -154.905997, 19.78032447],
        'start': '2013-01-01T00:00:00Z',
        'end': '2026-01-01T00:00:00Z',
    },
    'aira': {
        'path': 163,
        'bbox': [130.237126, 31.2178755, 131.080674, 31.9365244],
        'start': '2013-01-01T00:00:00Z',
        'end': '2026-01-01T00:00:00Z',
    },
}


def bbox_to_wkt(min_lon: float, min_lat: float, max_lon: float, max_lat: float) -> str:
    return f'POLYGON(({min_lon} {min_lat},{max_lon} {min_lat},{max_lon} {max_lat},{min_lon} {max_lat},{min_lon} {min_lat}))'


def get_granules(path: int, start: str, end: str, bbox: tuple[float, float, float, float]) -> list[str]:
    results = asf_search.geo_search(
        platform=asf_search.PLATFORM.SENTINEL1,
        processingLevel=asf_search.PRODUCT_TYPE.RAW,
        beamMode=asf_search.BEAMMODE.IW,
        # polarization=asf_search.POLARIZATION.VV_VH,
        relativeOrbit=path,
        start=start,
        end=end,
        intersectsWith=bbox_to_wkt(*bbox),
    )
    return [result.properties['sceneName'] for result in results]


def submit_job(granules: list[str], bbox: tuple[float, float, float, float]) -> hyp3_sdk.Job:
    url = 'https://hyp3-lavas.asf.alaska.edu'
    hyp3 = hyp3_sdk.HyP3(url)
    prepared_job = {
        'job_type': 'SRG_TIME_SERIES',
        'job_parameters': {
            'granules': granules,
            'bounds': bbox,
        }
    }
    pprint.pprint(prepared_job)
    # job = hyp3.submit_prepared_jobs(prepared_job)[0]
    # print(f'{url}/jobs/{job.job_id}')
    # return job


def get_args():
    parser = argparse.ArgumentParser()
    sub_parsers = parser.add_subparsers(required=True)

    site_parser = sub_parsers.add_parser('site')
    site_parser.add_argument('site', choices=sites.keys())

    search_parser = sub_parsers.add_parser('search')
    search_parser.add_argument('bbox', type=float, nargs=4)
    search_parser.add_argument('path', type=int)
    search_parser.add_argument('start')
    search_parser.add_argument('end')

    args = parser.parse_args()
    if args.site:
        return argparse.Namespace(**sites[args.site])
    return args


def main():
    args = get_args()
    granule_names = get_granules(args.path, args.start, args.end, args.bbox)
    _ = submit_job(granule_names, args.bbox)


if __name__ == '__main__':
    main()
