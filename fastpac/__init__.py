import logging
import sys

try:
    from systemd.journal import JournalHandler
    have_systemd = True
except:
    have_systemd = False

_root_logger = logging.getLogger(__name__)
_fmt = logging.Formatter(
    '{asctime} {levelname} {filename}:{lineno}: {message}',
    datefmt='%b %d %H:%M:%S',
    style='{'
)

if sys.stdout.isatty():
    _hnd = logging.StreamHandler()
    _root_logger.setLevel(logging.DEBUG)
elif not have_systemd:
    _hnd = logging.StreamHandler()
else:
    _hnd = JournalHandler()

_hnd.setFormatter(_fmt)
_root_logger.addHandler(_hnd)
