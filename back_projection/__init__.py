"""Process L0 Raw Products using a back projection algorithm"""

from importlib.metadata import PackageNotFoundError, version

from back_projection.process import back_projection

try:
    __version__ = version(__name__)
except PackageNotFoundError:
    print(f'{__name__} package is not installed!\n'
          f'To install in editable/develop mode (from the repo\'s root):\n'
          f'   python -m pip install -e .[develop]\n'
          f'Or, to just get the version number use:\n'
          f'   python setup.py --version')

__all__ = [
    '__version__',
    'back_projection',
]
