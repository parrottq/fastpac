from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from os.path import isfile

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
        print(f"'{name}' could not be found")
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

        print(f"Finishe downloading '{package_mirror}'")
        # Next package
        break


if __name__ == "__main__":
    #from argparse import ArgumentParser
    #parser = ArgumentParser()
    #parser.add_argument("-w", "--workers", default=4, help="Number of parallel downloads")
    #parser.add_argument(
    #print(parser.parse_args())
    from sys import stdin
    package_names = set()
    for name in stdin:
        package_names.add(name.strip(" \n").split(" ")[0])
    package_names = list(sorted(package_names))

    # List of mirrors to use
    #mirrorlist = get_mirrorlist_online("https://www.archlinux.org/mirrors/status/json/")
    # Default location looks at mirrors in /etc/pacman.d/mirrorlist
    offline_mirrors = get_mirrorlist_offline()

    # This contains repos and their package databases.
    #
    # repos_provider is a generator that will fetch databases continuously. HybridGenerator is
    # a class that acts like self expanding list based off the results of a generator. The result
    # is a list of databases that expands when more are needed. databases is a list of dicts containing
    # 3 things, "name": the name of the repo eg. "core", "mirror": the url to the mirror it was fetched
    # from (optional right now), and "db": a databases.Repo object. It can be a generator as it is here
    databases = HybridGenerator(repos_provider(offline_mirrors, ["core", "extra", "community", "multilib"]))
    databases_lock = Lock()

    # What mirror should the package be downloaded from? There are a variety of preimplement ways in
    # fastpac.mirrorlist. Some implementations will run out of mirrorrs to select from if not enough
    # are present. This one will chose the mirror that has been used the least, taking into account
    # package size. CapPicker will assign a virtual cap to each mirror.
    mirrorpicker = LeastUsedPicker(offline_mirrors)
    mirrorpicker_lock = Lock()

    # Destination of downloads
    dest = "dest/"

    with ThreadPoolExecutor(max_workers=4) as pool:
        for package_name in package_names:
            pool.submit(download_package, package_name, dest, databases, databases_lock, mirrorpicker, mirrorpicker_lock)
