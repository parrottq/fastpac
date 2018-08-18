# fastpac
Parallel pacman package downloader

## Manual installation (packaging to follow)
Create requisite directories and set up config file:

```bash
# useradd -r fastpac
# mkdir -p /var/cache/fastpac/{pkg,pkglists}
# chown -R fastpac:fastpac /var/cache/fastpac
# cp config.py /etc/fastpac.conf.py
```

## Usage

```bash
# su fastpac
$ pacman -Q > "/var/cache/fastpac/$(hostname)"
$ fastpac
```
