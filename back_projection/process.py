"""
projector processing
"""
import argparse
import logging
import os
from pathlib import Path
from zipfile import ZipFile

__version__ = 1.0

log = logging.getLogger(__name__)


def back_projection(granule: str, username: str, password: str) -> Path:
    """Create GSLCS and Convert them to tiffs for viewing

    Args:
        granule: granule name to be processed.
        username: hyp3 username
        password: hyp3 password
    """

    HOME = os.environ['PROC_HOME']

    # Make granules.list file to be read by sentinel_cpu.py
    # to download necessary granules
    file = open("granule.list", "w")
    print("GRANULES TO DOWNLOAD: ", granule)
    output_string = granule + ".zip\n"
    file.write(output_string)
    file.close()

    # Run the back_projection through sentinel_cpu.py VV
    run_backprojection = HOME + "/sentinel/sentinel_cpu.py --username \""
    run_backprojection += username + "\" --password \"" + password + "\""
    print("Command: ", run_backprojection)
    ret = os.system(run_backprojection)

    # Convert each gslc to a multiband tiff
    # (band 1: complex, band 2: real, band 3: amplitude)
    make_tiff = "python3 " + HOME + "/make_tiff.py " + granule + ".geo "
    make_tiff += "elevation.dem.rsc " + granule
    print(make_tiff + "_VV.tiff")
    ret = os.system(make_tiff + "_VV.tiff")

    move_vv_file = "mv *.geo "+HOME+"/output/"+granule+"_VV.geo"
    ret = os.system(move_vv_file)

    # Run the back_projection through sentinel_cpu.py VH
    run_backprojection += " --polarization vh --use_existing_data True"
    print("Command: ", run_backprojection)
    ret = os.system(run_backprojection)

    # Convert each gslc to a multiband tiff
    # (band 1: complex, band 2: real, band 3: amplitude)
    print(make_tiff + "_VH.tiff")
    ret = os.system(make_tiff + "_VH.tiff")

    move_vh_file = "mv *.geo "+HOME+"/output/"+granule+"_VH.geo"
    ret = os.system(move_vh_file)

    # Remove all of the temporary files
    remove_files = "rm *.list *.EOF *.dem *.orbtiming "
    remove_files += "*.full latloncoords preciseorbitfiles "
    remove_files += "precise_orbtiming params"
    ret = os.system(remove_files)
    remove_SAFE = "rm -rf *.SAFE"
    ret = os.system(remove_SAFE)
    move_rsc_files = "mv elevation.dem.rsc "+HOME+"/output/"
    ret = os.system(move_rsc_files)
    ret = os.system("rm *.rsc")
    print(ret)

    with ZipFile(granule + ".zip", "w") as zipObj:
        for folder_name, sub_folders, filenames in os.walk(HOME+"/output/"):
            for filename in filenames:
                file_path = os.path.join(folder_name, filename)
                zipObj.write(file_path)

    return granule+".zip"


def main():
    """back_projection entrypoint"""
    parser = argparse.ArgumentParser(
        prog='back_projection',
        description=__doc__,
    )
    parser.add_argument("granule", type=str,
                        help="granule name to be processed")
    parser.add_argument("--username", type=str,
                        help="hyp3 username")
    parser.add_argument('--password', type=str,
                        help="hyp3 password")
    parser.add_argument('--version', action='version',
                        version=f'%(prog)s {__version__}')
    args = parser.parse_args()

    return back_projection(args.granule, args.username, args.password)


if __name__ == "__main__":
    product = main()
    print(product)
