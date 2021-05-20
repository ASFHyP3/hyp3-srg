"""
projector processing for HyP3
"""
import os
import logging
from argparse import ArgumentParser
from pathlib import Path

from hyp3lib.aws import upload_file_to_s3
from hyp3lib.image import create_thumbnail

import back_projection

__version__ = 1.0

HOME = os.environ['PROC_HOME']

def main():
    """
    HyP3 entrypoint for back_projection
    """
    parser = ArgumentParser()
    parser.add_argument("granule", metavar='granule', type=str,
                        help="name of granule to be processed.")
    parser.add_argument('--bucket', help='AWS S3 bucket HyP3 for upload the final product(s)')
    parser.add_argument('--bucket-prefix', default='', help='Add a bucket prefix to product(s)')
    parser.add_argument("--username", type=str,
                        help="hyp3 username")
    parser.add_argument('--password', type=str, 
                        help="hyp3 password")

    args = parser.parse_args()

    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)

    product_path_string = back_projection.back_projection(
            granule=args.granule,
            username=args.username,
            password=args.password,
    )

    print(os.listdir(HOME + "/output"))
    
    if args.bucket:
        upload_file_to_s3(Path(product_path_string), args.bucket, args.bucket_prefix)

if __name__ == '__main__':
    main()
 
