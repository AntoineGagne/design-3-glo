import os


def compare_objects(object_1, object_2):
    """Compare two object for equality.

    :param object_1: The first object
    :param object_2: The second object
    :raises AssertionError: If the two object are not equal or not of the same
                            types
    """
    assert (isinstance(object_1, object_2.__class__) and
            object_1.__dict__ == object_2.__dict__)


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
