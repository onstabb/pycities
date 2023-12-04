import os
import sys
import time
import zipfile
from http.client import HTTPMessage
from typing import Tuple, Union

from urllib.request import urlretrieve
from urllib.parse import urljoin


_start_time = 0.0


def _on_chunk_received(count: int, block_size: int, total_size: int) -> None:
    global _start_time

    if count == 0:
        _start_time = time.time()
        return

    duration_sec = time.time() - _start_time
    progress_size = int(count * block_size)
    speed_kbs = int(progress_size / (1024 * duration_sec))
    percent = min(int(count * block_size * 100 / total_size), 100)
    sys.stdout.write(
        f"\rDownload...{percent}%, {progress_size / (1024 * 1024):.2f} MB, {speed_kbs} KB/s, {duration_sec:.0f}s"
    )
    sys.stdout.flush()
    if percent >= 100:
        print()


def download_file(filename: str, directory: Union[os.PathLike, str], url: str,) -> Tuple[str, HTTPMessage]:
    return urlretrieve(
        urljoin(url, filename),
        filename=os.path.join(directory, filename),
        reporthook=_on_chunk_received
    )


def file_unzip(to_directory: Union[os.PathLike, str], filepath: Union[str, os.PathLike]) -> None:
    with zipfile.ZipFile(filepath, "r") as zip_file:
        zip_file.extractall(path=to_directory)

