import pytest

import config
import datadownload


@pytest.mark.parametrize(
    "filename",
    [
        config.CITIES_ARCHIVE_FILENAME,
        config.COUNTRIES_FILENAME,
        config.ADMINISTRATIVE_FILENAME,
    ]
)
def test_download_file(temp_data_path, filename):
    downloaded_file_path = temp_data_path / filename
    datadownload.download_file(filename=filename, directory=temp_data_path, url=config.GEONAMES_URL)
    assert downloaded_file_path.exists()


@pytest.mark.parametrize(
    "filename, expected_filename",
    [
        (config.CITIES_ARCHIVE_FILENAME, config.CITIES_FILENAME),
    ]
)
def test_file_unzip(data_dir, temp_data_path, filename, expected_filename):
    datadownload.file_unzip(temp_data_path, data_dir / filename)
    extracted_file_path = temp_data_path / expected_filename
    assert extracted_file_path.exists()
