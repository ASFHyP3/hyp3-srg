import logging
import netrc
import os
import subprocess
from pathlib import Path
from platform import system
from typing import List, Optional, Tuple
from zipfile import ZipFile

import asf_search
from hyp3lib.get_orb import downloadSentinelOrbitFile
from shapely.geometry import Polygon, shape


log = logging.getLogger(__name__)
ESA_HOST = 'dataspace.copernicus.eu'
EARTHDATA_HOST = 'urs.earthdata.nasa.gov'


def get_proc_home() -> Path:
    """Get the PROC_HOME environment variable, which is the location of the SRG modules.

    Returns:
        Path to the PROC_HOME directory
    """
    proc_home = os.environ.get('PROC_HOME', None)
    if proc_home is None:
        raise ValueError('PROC_HOME environment variable is not set. Location of Stanford modules is unknown.')
    return Path(proc_home)


def get_netrc() -> Path:
    """Get the location of the netrc file.

    Returns:
        Path to the netrc file
    """
    netrc_name = '_netrc' if system().lower() == 'windows' else '.netrc'
    netrc_file = Path.home() / netrc_name
    return netrc_file


def set_creds(service, username, password) -> None:
    """Set username/password environmental variables for a service.
    username/password are set using the following format:
    SERVICE_USERNAME, SERVICE_PASSWORD

    Args:
        service: Service to set credentials for
        username: Username for the service
        password: Password for the service
    """
    if username is not None:
        os.environ[f'{service.upper()}_USERNAME'] = username

    if password is not None:
        os.environ[f'{service.upper()}_PASSWORD'] = password


def find_creds_in_env(username_name, password_name) -> Tuple[str, str]:
    """Find credentials for a service in the environment.

    Args:
        username_name: Name of the environment variable for the username
        password_name: Name of the environment variable for the password

    Returns:
        Tuple of the username and password found in the environment
    """
    if username_name in os.environ and password_name in os.environ:
        username = os.environ[username_name]
        password = os.environ[password_name]
        return username, password

    return None, None


def find_creds_in_netrc(service) -> Tuple[str, str]:
    """Find credentials for a service in the netrc file.

    Args:
        service: Service to find credentials for

    Returns:
        Tuple of the username and password found in the netrc file
    """
    netrc_file = get_netrc()
    if netrc_file.exists():
        netrc_credentials = netrc.netrc(netrc_file)
        if service in netrc_credentials.hosts:
            username = netrc_credentials.hosts[service][0]
            password = netrc_credentials.hosts[service][2]
            return username, password

    return None, None


def get_esa_credentials() -> Tuple[str, str]:
    """Get ESA credentials from the environment or netrc file.

    Returns:
        Tuple of the ESA username and password
    """
    username, password = find_creds_in_env('ESA_USERNAME', 'ESA_PASSWORD')
    if username and password:
        return username, password

    username, password = find_creds_in_netrc(ESA_HOST)
    if username and password:
        return username, password

    raise ValueError(
        'Please provide Copernicus Data Space Ecosystem (CDSE) credentials via the '
        'ESA_USERNAME and ESA_PASSWORD environment variables, or your netrc file.'
    )


def get_earthdata_credentials() -> Tuple[str, str]:
    """Get NASA EarthData credentials from the environment or netrc file.

    Returns:
        Tuple of the NASA EarthData username and password
    """
    username, password = find_creds_in_env('EARTHDATA_USERNAME', 'EARTHDATA_PASSWORD')
    if username and password:
        return username, password

    username, password = find_creds_in_netrc(EARTHDATA_HOST)
    if username and password:
        return username, password

    raise ValueError(
        'Please provide NASA EarthData credentials via the '
        'EARTHDATA_USERNAME and EARTHDATA_PASSWORD environment variables, or your netrc file.'
    )


def download_raw_granule(granule_name: str, output_dir: Path, unzip: bool = False) -> Tuple[Path, Polygon]:
    """Download a S1 granule using asf_search. Return its path
    and buffered extent.

    Args:
        granule_name: Name of the granule to download
        output_dir: Directory to save the granule in
        unzip: Unzip the granule if it is a zip file

    Returns:
        Tuple of the granule path and its extent as a Polygon
    """
    username, password = get_earthdata_credentials()
    session = asf_search.ASFSession().auth_with_creds(username, password)
    if not granule_name.endswith('-RAW'):
        granule_name += '-RAW'

    result = asf_search.granule_search([granule_name])[0]
    bbox = shape(result.geojson()['geometry'])

    zip_path = output_dir / f'{granule_name[:-4]}.zip'
    if not unzip:
        out_path = zip_path
        if not out_path.exists():
            result.download(path=output_dir, session=session)
    else:
        out_path = output_dir / f'{granule_name[:-4]}.SAFE'
        if not out_path.exists() and not zip_path.exists():
            result.download(path=output_dir, session=session)

        if not out_path.exists():
            with ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall('.')

        if zip_path.exists() and unzip:
            zip_path.unlink()

    return out_path, bbox


def download_orbit(granule_name: str, output_dir: Path) -> Path:
    """Download a S1 orbit file. Prefer using the ESA API,
    but fallback to ASF if needed.

    Args:
        granule_name: Name of the granule to download
        output_dir: Directory to save the orbit file in

    Returns:
        Path to the downloaded orbit file
    """
    orbit_path, _ = downloadSentinelOrbitFile(granule_name, str(output_dir), esa_credentials=get_esa_credentials())
    return orbit_path


def call_stanford_module(local_name, args: List = [], work_dir: Optional[Path] = None) -> None:
    """Call a Stanford Processor modules (via subprocess) with the given arguments.

    Args:
        local_name: Name of the module to call (e.g. 'sentinel/sentinel_scene_cpu.py')
        work_dir: Directory to run the module in
        args: List of arguments to pass to the module
    """
    if work_dir is None:
        work_dir = Path.cwd()

    proc_home = get_proc_home()
    script = proc_home / local_name
    args = [str(x) for x in args]
    print(f'Calling {local_name} {" ".join(args)} in directory {work_dir}')
    subprocess.run([script, *args], cwd=work_dir, check=True)


def how_many_gpus():
    """Get the number of GPUs available on the system using Stanford script."""
    cmd = (get_proc_home() / 'sentinel' / 'howmanygpus').resolve()
    proc = subprocess.Popen(str(cmd), stdout=subprocess.PIPE, shell=True)
    (param, err) = proc.communicate()
    ngpus = int(str(param, 'UTF-8').split()[0])
    return ngpus
