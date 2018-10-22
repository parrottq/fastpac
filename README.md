# fastpac
Parallel pacman package downloader

## Manual installation (packaging to follow)
Create requisite directories and set up config file:

```
# python setup.py install
# useradd -r fastpac
# mkdir -p /var/cache/fastpac/{pkg,pkglists}
# chown -R fastpac:fastpac /var/cache/fastpac
# cp config.py /etc/fastpac.conf.py
```

## Usage

```
# su fastpac
$ pacman -Q > "/var/cache/fastpac/packagelists/$(hostname)"
$ fastpac
```

## Hacking

Contributions are welcome! All new code should be tested using our pytest
testing system, which you can run with the shell command `py.test` in
the root of the repository.
