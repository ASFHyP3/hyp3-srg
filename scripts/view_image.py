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


def plot_image(file_path: Path, rsc_path: Path):
    info = parse_rsc(rsc_path)
    ftype, data = load_image(file_path, info)
    title = file_path.name

    cmap = 'gray'
    if ftype == 'int':
        cmap = 'hsv'

    f, ax = plt.subplots(1, 1, figsize=(15, 10))
    im = ax.imshow(data, cmap=cmap, vmin=float(np.percentile(data, 1)), vmax=float(np.percentile(data, 99)))
    f.colorbar(im, ax=ax, shrink=0.5)
    ax.set_title(title)
    plt.tight_layout()
    plt.show()


def plot_hist(ax, array, color, label):
    ax.hist(
        array.flatten(),
        bins=50,
        color=color,
        label=label,
        alpha=0.25,
        range=(np.percentile(array, 1), np.percentile(array, 99)),
    )


def plot_diff(file_path: Path, file_path2: Path, rsc_path: Path, save: bool = False):
    info = parse_rsc(rsc_path)
    ftype, data = load_image(file_path, info)
    title = file_path.name

    ftype2, data2 = load_image(file_path2, info)
    if ftype != ftype2:
        raise ValueError('Files must be of the same type to plot the difference.')
    diff = np.abs(data - data2)
    title = f'{file_path}\n-\n{file_path2}'

    cmap = 'gray'
    if ftype == 'int':
        cmap = 'hsv'

    f, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 10))
    im = ax1.imshow(diff, cmap=cmap, vmin=np.percentile(diff, 1), vmax=np.percentile(diff, 99))
    plot_hist(ax2, diff, 'black', 'Difference')
    f.colorbar(im, ax=ax1, shrink=0.5)
    ax1.set_title(title)
    plt.tight_layout()
    if not save:
        plt.show()
    else:
        out_path = file_path.parent / f'{file_path.stem}_minus_{file_path2.stem}.png'
        plt.savefig(out_path, dpi=300)
        print(f'Saved figure to {out_path}')
    plt.close(f)


def plots():
    image1 = Path('stanford/raw/S1A_IW_RAW__0SDV_20241006T161640_20241006T161717_055984_06D8A0_FC33.geo')
    image2s = list(Path('hawaii_old').glob('*.geo'))
    rsc = Path('stanford/elevation.dem.rsc')
    for image2 in image2s:
        plot_diff(image1, image2, rsc, save=True)


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
    if args.file2 is None:
        plot_image(args.file, args.rsc)
    else:
        plot_diff(args.file, args.file2, args.rsc)


if __name__ == '__main__':
    main()
