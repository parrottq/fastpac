import argparse
import logging
from threading import Lock
from typing import Any, Dict, List, Set
from pathlib import Path
import runpy
import sys
import traceback

from fastpac.mirror import get_mirrorlist_online, get_mirrorlist_offline
from fastpac.search import find_package, repos_provider
from fastpac.util import HybridGenerator, ThreadPoolExecutorStackTraced
from fastpac.download import assemble_package_url, download_file_to_path
from fastpac.picker import *


log = logging.getLogger('fastpac.__main__')


def download_package(name, dest, databases, databases_lock, mirrorpicker, mirrorpicker_lock):
    # find_package returns the filename for the current version and
    # its repo of residence. Both are needed to make the download url
    with databases_lock:
        package_info = find_package(name, databases, limit=8) # 8 because 4 different repo type * 2

    # find_package will return None if no package is in the database
    if not package_info:
        log.warning('%r could not be found', name)
        return

    # If it is already present we skip this package
    filename = package_info.filename
    if (dest / filename).is_file():
        log.debug('%r already exists', filename)
        return

    # Try downloading a package from a mirror until one works
    while True:
        # Picking a mirror to use
        with mirrorpicker_lock:
            mirror = mirrorpicker.next(size=int(package_info.size))

        # Combine the mirror url with info from databases to make a download url
        package_mirror = assemble_package_url(package_info, mirror)

        # Download
        log.info('Downloading %r from %s', filename, package_mirror)
        try:
            download_file_to_path(package_mirror, dest / filename)
        except Exception as e:
            log.exception(e)
            # Go to next mirror

        log.info('Finished downloading %s', package_mirror)
        # Next package
        break


def load_config(path: Path) -> Dict[str, Any]:
    """
    Load a runpy based config from a Path

    Parameters:
    path -- Path object to load the config from
    """
    init_globals = {k: v for (k, v) in globals().items()
                    if k.endswith('Picker') or k.endswith('Generator')
                    or k.startswith('get_mirrorlist')
                    or k.endswith('provider')}
    return runpy.run_path(path, init_globals=init_globals)


def make_package_list(path: Path) -> Set[str]:
    """
    Makes the package list from a directory with newline delimited
    files.

    Parameters:
    path -- Path object to directory with package list files
    """
    packages = set()
    for child in path.iterdir():
        with child.open('r') as h:
            packages.update(s.partition(' ')[0] for s in h.readlines())
    return packages


class PathFileType:
    def __init__(self):
        pass

    def __call__(self, string):
        path = Path(string)
        if not path.is_file():
            raise argparse.ArgumentTypeError(f'{string} is not a file')
        return path


def parse_args(args: List[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument('--config-file', type=PathFileType(),
                   default='/etc/fastpac.conf.py', help='Path to config file')
    p.add_argument('--log-level', default=None, help='Log level')
    return p.parse_args()


def main(args: argparse.Namespace):
    config = load_config(args.config_file)
    if args.log_level:
        logging.getLogger('fastpac').setLevel(args.log_level.upper())
    package_names = make_package_list(Path(config['package_list_dir']))
    package_names = sorted(package_names)

    databases_lock = Lock()
    mirrorpicker_lock = Lock()

    dest = Path(config['download_dir'])

    if not dest.is_dir():
        raise ValueError(f'download_dir {dest} is not a directory')

    with ThreadPoolExecutorStackTraced(max_workers=config['workers']) as pool:
        futures = []
        for package_name in package_names:
            futures.append(pool.submit(download_package, package_name, dest, config['databases'], databases_lock, config['mirrorpicker'], mirrorpicker_lock))
        for future in futures:
            future.result()


if __name__ == "__main__":
    main(parse_args(sys.argv[1:]))
