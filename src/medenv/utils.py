# coding: utf-8
"""
This script belongs to the medenv package
Copyright (C) 2022 Jeremy Fix

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
# Standard imports
import pathlib
import urllib
import shutil
import gzip
import logging

# External imports
import tqdm

_BASEDIR = pathlib.Path.home() / ".medenv"

# my_hook comes for the tqdm examples


def my_hook(t):
    """Wraps tqdm instance.
    Don't forget to close() or __exit__()
    the tqdm instance once you're done with it (easiest using `with` syntax).
    Example
    -------
    >>> with tqdm(...) as t:
    ...     reporthook = my_hook(t)
    ...     urllib.urlretrieve(..., reporthook=reporthook)
    """
    last_b = [0]

    def update_to(b=1, bsize=1, tsize=None):
        """
        b  : int, optional
            Number of blocks transferred so far [default: 1].
        bsize  : int, optional
            Size of each block (in tqdm units) [default: 1].
        tsize  : int, optional
            Total size (in tqdm units). If [default: None] or -1,
            remains unchanged.
        """
        if tsize not in (None, -1):
            t.total = tsize
        displayed = t.update((b - last_b[0]) * bsize)
        last_b[0] = b
        return displayed

    return update_to


def download_url(url, filename=None):
    logging.debug(f"Downloading from {url}")
    if filename is not None and filename.exists():
        return filename
    with tqdm.tqdm(unit="B", unit_scale=True, unit_divisor=1024, miniters=1) as t:
        local_filename, headers = urllib.request.urlretrieve(
            url, filename, reporthook=my_hook(t)
        )
    return local_filename


def _extract_gz(filepath: pathlib.Path, target: pathlib.Path):
    with gzip.open(filepath, "rb") as f_in:
        with open(target, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)


_ARCHIVE_EXTRACTORS = {"gzip": _extract_gz, "raw": lambda: None}


def download_and_extract(url, archivetype, name):
    if not _BASEDIR.exists():
        _BASEDIR.mkdir()
    f_out = _BASEDIR / name
    if f_out.exists():
        logging.debug(f"Data already extracted to {f_out}")
        return f_out

    local_filename = download_url(url)
    logging.debug(f"Data temporarily saved to {local_filename}")
    _ARCHIVE_EXTRACTORS[archivetype](local_filename, f_out)
    logging.debug(f"Data extracted to {f_out}")
    return f_out
