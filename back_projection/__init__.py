"""This is a program to process L0 Raw Products using a back projection algorithm"""

from importlib.metadata import PackageNotFoundError, version

from back_projection.process import back_projection

try:
    __version__ = version(__name__)
except PackageNotFoundError:
    print(f'{__name__} package is not installed!\n'
          f'Install in editable/develop mode via (from the top of this repo):\n'
          f'   python -m pip install -e .[develop]\n'
          f'Or, to just get the version number use:\n'
          f'   python setup.py --version')

__all__ = [
    '__version__',
    'back_projection',
]
