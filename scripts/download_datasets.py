from errno import EEXIST
from os import makedirs
from urllib.request import urlretrieve
from threading import Thread


DATA_FILES_DIRECTORY = 'data'
DATA_URL_FILE = 'datasets.txt'
GOOGLE_DRIVE_DOWNLOAD_LINK = 'https://drive.google.com/uc?export=download&id='


def download_datasets(file_name: str):
    """Download all the datasets specified in the file.

    :param file_name: The name of the file containing the datasets IDs
    :type file_name: str
    """
    threads = []
    url_file = open(file_name, 'r')
    for line in url_file:
        data_name, data_id = line.split()
        thread = Thread(target=download_dataset,
                        args=(data_id, data_name),
                        daemon=True)
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()


def download_dataset(dataset_id: str, data_name: str):
    """Download the dataset from the Google Drive with the corresponding ID
       and the corresponding name.

       :param dataset_id: The ID of the dataset on Google Drive
       :type dataset_id: str
       :param data_name: The name of the file on the Google Drive
       :type data_name: str
    """
    file_name, _ = urlretrieve('{0}{1}'.format(GOOGLE_DRIVE_DOWNLOAD_LINK,
                                               dataset_id),
                               './{0}/{1}.tar.gz'.format(DATA_FILES_DIRECTORY,
                                                         data_name))


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
    create_directory(DATA_FILES_DIRECTORY)
    download_datasets(DATA_URL_FILE)
