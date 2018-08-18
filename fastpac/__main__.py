import argparse
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from typing import Any, Dict, List, Set
from pathlib import Path
import runpy
import sys

from fastpac.mirror import get_mirrorlist_online, get_mirrorlist_offline
from fastpac.search import find_package, repos_provider
from fastpac.util import HybridGenerator
from fastpac.download import assemble_package_url, download_file_to_path
from fastpac.picker import LeastUsedPicker


def download_package(name, dest, databases, databases_lock, mirrorpicker, mirrorpicker_lock):

    # find_package returns the filename for the current version and
    # its repo of residence. Both are needed to make the download url
    with databases_lock:
        package_info = find_package(name, databases, limit=8) # 8 because 4 different repo type * 2

    # find_package will return None if no package is in the database
    if not package_info:
        print(f'{name!r} could not be found')
        return

    # If it is already present we skip this package
    filename = package_info["filename"]
    if isfile(f"{dest}{filename}"):
        print(f"'{filename}' already exists")
        return

    # Try downloading a package from a mirror until one works
    while True:
        # Picking a mirror to use
        with mirrorpicker_lock:
            mirror = mirrorpicker.next(size=int(package_info["size"]))

        # Combine the mirror url with info from databases to make a download url
        package_mirror = assemble_package_url(package_info, mirror)

        # Download
        print(f"Downloading '{filename}' from {package_mirror}")
        try:
            download_file_to_path(package_mirror, f"{dest}{filename}")
        except Exception:
            print(f"Download '{package_mirror}' failed")
            # Go to next mirror
            continue

        print(f"Finished downloading '{package_mirror}'")
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
    p.add_argument('--config-file', type=PathFileType(), help='Path to config file')
    return p.parse_args()


def main(args: argparse.Namespace):
    config = load_config(args.config_file)
    package_names = make_package_list(Path(config['package_list_dir']))
    package_names = sorted(package_names)

    databases_lock = Lock()
    mirrorpicker_lock = Lock()

    dest = Path(config['download_dir'])

    if not dest.is_dir():
        raise ValueError(f'download_dir {dest} is not a directory')

    with ThreadPoolExecutor(max_workers=4) as pool:
        for package_name in package_names:
            pool.submit(download_package, package_name, dest, config['databases'], databases_lock, config['mirrorpicker'], mirrorpicker_lock)


if __name__ == "__main__":
    main(parse_args(sys.argv[1:]))
