"""
projector processing
"""

import os
import argparse
import logging
from pathlib import Path

#from back_projection import __version__

__version__ = 1.0

log = logging.getLogger(__name__)

HOME = os.environ['PROC_HOME']

def back_projection(granule_list: str, username: str, password: str, polarization: str) -> Path:
    """Create GSLCS and Convert them to tiffs for viewing

    Args:
        granule_list: a list of granule names to be processed.
        username: hyp3 username
        password: hyp3 password
        polarization: Choose either vv or vh. Default is vv.
    """

    # Make granules.list file to be read by sentinel_cpu.py to download necessary granules
    filename = "granule.list"
    output_string = ""
    for granule in granule_list:
        output_string += (granule + ".zip" + "\n")
    
    file = open(filename, "w")
    print("GRANULES TO DOWNLOAD: ", output_string)
    file.write(output_string)
    file.close()

    # Run the back_projection through sentinel_cpu.py 
    run_backprojection  = HOME + "/sentinel/sentinel_cpu.py --username \""
    run_backprojection += username + "\" --password \"" + password + "\" --polarization " + polarization
    print("Command: ", run_backprojection)
    ret = os.system(run_backprojection)

    # Convert each gslc to a multiband tiff
    # (band 1: complex, band 2: real, band 3: amplitude)
    for granule in granule_list:
        make_tiff = "python3 " + HOME + "/make_tiff.py " + granule + ".geo " + "elevation.dem.rsc"
        print(make_tiff)
        ret = os.system(make_tiff)

    # Remove all of the temporary files
    remove_files  = "rm *.list *.geo *.EOF *.dem *.rsc *.orbtiming "
    remove_files += "*.full latloncoords preciseorbitfiles precise_orbtiming params"
    ret = os.system(remove_files)
    remove_SAFE = "rm -rf *.SAFE"
    ret = os.system(remove_SAFE)

    # Return the paths to the tiffs
    products = []
    for granule in granule_list:
        products.append(HOME + "/output/" + granule + ".tiff")

    return products

def main():
    """back_projection entrypoint"""
    parser = argparse.ArgumentParser(
        prog='back_projection',
        description=__doc__,
    )
    parser.add_argument("granule_list", metavar='N', type=str, nargs='+',
                        help="list 1 or more granule names to be processed.")
    parser.add_argument("--username", type=str,
                        help="hyp3 username")
    parser.add_argument('--password', type=str, 
                        help="hyp3 password")
    parser.add_argument('--polarization', type=str, default="vv",
                        help="Specify vv or vh Polarization. Default=vv")
    parser.add_argument('--version', action='version', version=f'%(prog)s {__version__}')
    args = parser.parse_args()

    return back_projection(args.granule_list, args.username, args.password)

if __name__ == "__main__":
    products = main()
    print(products)