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

# What mirror should the package be downloaded from? There are a variety of preimplement ways in
# fastpac.mirrorlist. Some implementations will run out of mirrorrs to select from if not enough
# are present. This one will chose the mirror that has been used the least, taking into account
# package size. CapPicker will assign a virtual cap to each mirror.
mirrorpicker = LeastUsedPicker(offline_mirrors)

# Directory which the agents on remote systems put their package lists in
package_list_dir = '/var/cache/fastpac/packagelists'

# Destination of downloads
download_dir = '/var/cache/fastpac/pkg'

workers = 4
