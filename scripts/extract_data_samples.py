"""Script that extracts the data files."""

from errno import EEXIST
from os import listdir, makedirs, getcwd
from os.path import isfile, join
from threading import Thread

import tarfile
import sys


DATA_FILES_DIRECTORY = 'data'
SAMPLES_DIRECTORY_NAME = 'samples'


def find_files(directory_path: str):
    """Find the file in a given directory.

    :param directory_path: The path of the directory
    :type directory_path: str
    :return: A generator with all the given files
    """
    return (join(directory_path, listed_file)
            for listed_file in listdir(directory_path)
            if isfile(join(directory_path, listed_file))
            and listed_file.endswith('tar.gz'))


def extract_data_files(data_files):
    """Extract the data files in the given directory.

    :param data_files: The data files to extract
    :param directory_path: The path in which to extract the data files
    :type directory_path: str
    """
    threads = []
    for data_file in data_files:
        thread = Thread(target=extract_data_file,
                        args=(data_file,),
                        daemon=True)
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()


def extract_data_file(data_file):
    """Extract the given data file in the given directory.

    :param data_file: The data file to extract
    """
    archive = tarfile.open(data_file, 'r:gz')
    archive.extractall()
    archive.close()


def create_directory(path: str):
    """Create a directory at the given path if it doesn't exist.

    :param path: The path to the directory
    :type path: str
    """
    try:
        makedirs(path)
    except OSError as exception:
        if exception.errno != EEXIST:
            raise


if __name__ == '__main__':
    PROJECT_PATH = sys.argv[1] if len(sys.argv) > 1 else getcwd()
    SAMPLES_DIRECTORY_PATH = join(PROJECT_PATH,
                                  SAMPLES_DIRECTORY_NAME)
    create_directory(SAMPLES_DIRECTORY_PATH)
    FILES = find_files(join(PROJECT_PATH, DATA_FILES_DIRECTORY))
    extract_data_files(FILES)
