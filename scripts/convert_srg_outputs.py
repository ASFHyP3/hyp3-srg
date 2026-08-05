import argparse
from pathlib import Path

import numpy as np
from osgeo import gdal


gdal.UseExceptions()


def parse_rsc(rsc_file: Path) -> dict:
    """Parse the metadata from an SRG RSC file

    Args:
        rsc_file: Path to the RSC file

    Returns:
        Dictionary with the metadata from the RSC file
    """
    types_dict = {
        'WIDTH': int,
        'FILE_LENGTH': int,
        'X_FIRST': float,
        'Y_FIRST': float,
        'X_STEP': float,
        'Y_STEP': float,
        'X_UNIT': str,
        'Y_UNIT': str,
        'Z_OFFSET': float,
        'Z_SCALE': float,
        'PROJECTION': str,
        'xstart': float,
        'ystart': float,
        'xend': float,
        'yend': float,
        'xsize': int,
        'ysize': int,
    }
    with open(rsc_file, 'r') as f:
        lines = f.readlines()
    rsc_dict = {}
    for line in lines:
        key, value = line.strip().split()
        rsc_dict[key] = types_dict[key](value)
    return rsc_dict


def parse_sbas_list(sbas_list: Path) -> tuple[list[str], list[list[str]]]:
    """Parse the list of SBAS pairs from a SBAS list file

    Args:
        sbas_list: Path to the SBAS list file

    Returns:
        List with the names of the files in the SBAS list
        List with the pairs of files in the SBAS list
    """
    with open(sbas_list, 'r') as f:
        lines = f.readlines()
    pairs = [[Path(x).name for x in line.strip().split()[:2]] for line in lines]
    files = sorted(list(set([x for pair in pairs for x in pair])))
    return files, pairs


def write_geotiff(data: np.ndarray, info: dict, filename: Path, band_names: list[str] = None) -> None:
    """Write a numpy array to a GeoTIFF file

    Args:
        data: Numpy array with the data to be written
        info: Dictionary with the metadata from the DEM RSC file
        filename: Path to the output GeoTIFF file
        band_names: List with the names of the bands in the output GeoTIFF
    """
    if data.dtype == np.float32:
        dtype = gdal.GDT_Float32
    elif data.dtype == np.int16:
        dtype = gdal.GDT_Int16
    elif data.dtype == np.int32:
        dtype = gdal.GDT_Int32
    else:
        raise ValueError('Data type not supported')

    if len(data.shape) == 3:
        n_bands, n_rows, n_cols = data.shape
    else:
        n_bands = 1
        n_rows, n_cols = data.shape

    driver = gdal.GetDriverByName('GTiff')
    ds = driver.Create(str(filename), n_cols, n_rows, n_bands, dtype)
    ds.SetGeoTransform((info['X_FIRST'], info['X_STEP'], 0, info['Y_FIRST'], 0, info['Y_STEP']))
    ds.SetProjection('EPSG:4326')
    if n_bands == 1:
        ds.GetRasterBand(1).WriteArray(data)
    else:
        for i in range(n_bands):
            band = ds.GetRasterBand(i + 1)
            band.WriteArray(data[i, :, :])
            if band_names is not None:
                band.SetDescription(band_names[i])
            band.FlushCache()
            del band
    ds = None


def convert_single_band(file: Path, info: dict, dtype: np.dtype) -> None:
    """Convert a single-band SRG file to a GeoTIFF

    Args:
        file: Path to the SRG file
        info: Dictionary with the metadata from the DEM RSC file
        dtype: Numpy data type of the file
    """
    data = np.fromfile(file, dtype=dtype).reshape(info['FILE_LENGTH'], -1)
    write_geotiff(data, info, file.with_suffix('.tif'))


def convert_displacement(displacement_file: Path, info: dict, band_names: list[str]) -> None:
    """Convert the velocity file to separate GeoTIFFs for amplitude and displacement
    Save each date as a separate band

    Args:
        displacement_file: Path to the SRG displacement file
        info: Dictionary with the metadata from the DEM RSC file
        band_names: List with the dates of the SBAS pairs
    """
    data = np.fromfile(displacement_file, dtype=np.float32).reshape(-1, info['WIDTH'])

    amplitude = data[0::2, :]
    amplitude = amplitude.reshape(len(band_names), info['FILE_LENGTH'], info['WIDTH'])
    write_geotiff(amplitude, info, displacement_file.parent / 'amplitude.tif', band_names=band_names)

    displacement = data[1::2, :]
    displacement = displacement.reshape(len(band_names), info['FILE_LENGTH'], info['WIDTH'])
    write_geotiff(displacement, info, displacement_file.parent / 'displacement.tif', band_names=band_names)


def convert_velocity(velocity_file: Path, info: dict, band_names: list[str]) -> None:
    """Convert the velocity file to a GeoTIFF
    Save each date as a separate band

    Args:
        velocity_file: Path to the SRG velocity file
        info: Dictionary with the metadata from the DEM RSC file
        band_names: List with the dates of the SBAS pairs
    """
    data = np.fromfile(velocity_file, dtype=np.float32).reshape(-1, info['WIDTH'])
    velocity = data.reshape(len(band_names), info['FILE_LENGTH'], info['WIDTH'])
    write_geotiff(velocity, info, velocity_file.parent / 'velocity.tif', band_names=band_names)


def convert_files(sbas_dir: Path) -> None:
    """Convert the contents of a SRG SBAS directory to GeoTIFFs

    Args:
        sbas_dir: Path to the SBAS directory for a SRG run
    """
    info = parse_rsc(sbas_dir / 'dem.rsc')
    files, pairs = parse_sbas_list(sbas_dir / 'sbas_list')
    band_names = [x[17:25] for x in files][1:]
    convert_single_band(sbas_dir / 'dem', info, dtype=np.int16)
    convert_single_band(sbas_dir / 'npts', info, dtype=np.int32)
    convert_single_band(sbas_dir / 'stacktime', info, dtype=np.int32)
    convert_displacement(sbas_dir / 'displacement', info, band_names)
    convert_velocity(sbas_dir / 'velocity', info, band_names)


def main():
    """CLI for the convert_srg_outputs.py script

    Example:
        python convert_srg_outputs.py ./path/to/srg_sbas_directory
    """
    parser = argparse.ArgumentParser(description='Convert the contents of a SRG SBAS directory to GeoTIFF')
    parser.add_argument('directory', type=str, help='SRG SBAS directory')
    args = parser.parse_args()
    args.directory = Path(args.directory)
    convert_files(args.directory)


if __name__ == '__main__':
    main()
