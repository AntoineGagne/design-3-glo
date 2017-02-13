import os


def list_files(folder):
    """List all the files recursively within a given folder.

    :param folder: The folder to list
    :type folder: str
    :returns: A generator of the listed files
    .. Taken from:
       http://stackoverflow.com/questions/12420779/simplest-way-to-get-the-equivalent-of-find-in-python
    """
    for root, folders, files in os.walk(folder):
        for filename in files:
            yield os.path.join(root, filename)
