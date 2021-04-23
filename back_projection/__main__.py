"""
projector processing for HyP3
"""
import os
import logging
from argparse import ArgumentParser

# from hyp3lib.aws import upload_file_to_s3
# from hyp3lib.image import create_thumbnail

import back_projection

__version__ = 1.0

HOME = os.environ['PROC_HOME']

def main():
    """
    HyP3 entrypoint for back_projection
    """
    parser = ArgumentParser()
    parser.add_argument('--bucket', help='AWS S3 bucket HyP3 for upload the final product(s)')
    parser.add_argument('--bucket-prefix', default='', help='Add a bucket prefix to product(s)')

    parser.add_argument("granule_list", metavar='granule', type=str, nargs='+',
                        help="list 1 or more granule names to be processed.")
    parser.add_argument("--username", type=str,
                        help="hyp3 username")
    parser.add_argument('--password', type=str, 
                        help="hyp3 password")
    parser.add_argument('--polarization', type=str, default="vv",
                        help="Specify vv or vh Polarization. Default=vv")

    args = parser.parse_args()

    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)


    product_list = back_projection.back_projection(
            granule_list=args.granule_list,
            username=args.username,
            password=args.password,
            polarization=args.polarization
    )

    print(os.listdir(HOME + "/output"))
    
    # for product in product_list:
    #     if args.bucket:
    #         # upload_file_to_s3(product, args.bucket, args.bucket_prefix)


if __name__ == '__main__':
    main()
 