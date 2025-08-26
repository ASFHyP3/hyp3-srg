import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from convert_srg_outputs import parse_rsc


def load_image(file_path: Path, info: dict):
    suffix = file_path.suffix
    if suffix == '.geo':
        ftype = 'slc'
        data = np.fromfile(file_path, dtype=np.float32).reshape(info['FILE_LENGTH'], -1)
        real = data[:, 0::2]
        imag = data[:, 1::2]
        data = np.abs(real + 1j * imag)
    elif suffix == '.amp':
        ftype = 'amp'
        data = np.fromfile(file_path, dtype=np.float32).reshape(info['FILE_LENGTH'], -1)
    elif suffix == '.int':
        ftype = 'int'
        data = np.fromfile(file_path, dtype=np.float32).reshape(info['FILE_LENGTH'], -1)
        real = data[:, 0::2]
        imag = data[:, 1::2]
        data = np.angle(real + 1j * imag)
    elif suffix == '.unw':
        ftype = 'unw'
        data = np.fromfile(file_path, dtype=np.float32).reshape(info['FILE_LENGTH'], -1)
        data = data[:, data.shape[1] // 2 :]
    elif suffix == '.cc':
        ftype = 'cc'
        data = np.fromfile(file_path, dtype=np.float32).reshape(info['FILE_LENGTH'], -1)
        data = data[:, data.shape[1] // 2 :]
    elif suffix == '':
        name = file_path.name
        if name == 'dem':
            ftype = 'dem'
            data = np.fromfile(file_path, dtype=np.int16).reshape(info['FILE_LENGTH'], -1)
        elif name == 'npts':
            ftype = 'npts'
            data = np.fromfile(file_path, dtype=np.int32).reshape(info['FILE_LENGTH'], -1)
        elif name == 'stacktime':
            ftype = 'stacktime'
            data = np.fromfile(file_path, dtype=np.int32).reshape(info['FILE_LENGTH'], -1)
        elif name == 'velocity':
            raise NotImplementedError('Loading of velocity files not implemented.')
        elif name == 'displacement':
            raise NotImplementedError('Loading of displacement files not implemented.')
        else:
            raise ValueError(f'File {file_path} not recognized')
    else:
        raise ValueError(f'File {file_path} not recognized')
    return ftype, data


def plot_image(file_path: Path, rsc_path: Path, file_path2: Path | None = None):
    info = parse_rsc(rsc_path)
    ftype, data = load_image(file_path, info)
    title = file_path.name

    if file_path2 is not None:
        ftype2, data2 = load_image(file_path2, info)
        if ftype != ftype2:
            raise ValueError('Files must be of the same type to plot the difference.')
        data = data - data2
        title = f'Difference: {file_path.name} - {file_path2.name}'

    cmap = 'gray'
    if ftype in ['amp', 'slc']:
        data = 10 * np.log10(data)
    if ftype == 'int':
        cmap = 'hsv'

    f, ax = plt.subplots(1, 1, figsize=(10, 10))
    im = ax.imshow(data, cmap=cmap, vmin=float(np.percentile(data, 1)), vmax=float(np.percentile(data, 99)))
    f.colorbar(im, ax=ax, shrink=0.5)
    ax.set_title(title)
    plt.tight_layout()
    plt.show()


def main():
    """CLI for the convert_srg_outputs.py script

    Example:
        python convert_srg_outputs.py ./path/to/srg_sbas_directory
    """
    parser = argparse.ArgumentParser(description='Convert the contents of a SRG SBAS directory to GeoTIFF')
    parser.add_argument('file', type=Path, help='Path to file to display.')
    parser.add_argument('rsc', type=Path, help='Path to companion RSC file.')
    parser.add_argument(
        'file2',
        type=Path,
        help='Path a second file. Image displayed will be the difference between the two files.',
        nargs='?',
    )
    args = parser.parse_args()
    plot_image(args.file, args.rsc, args.file2)


if __name__ == '__main__':
    main()
