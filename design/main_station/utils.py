"""
References
    function get_latest_image :
        Code snippet from Stack Overflow, written by lemonhead: <http://stackoverflow.com/users/4582273/lemonhead>
        at : <http://stackoverflow.com/questions/30882796/how-to-read-the-latest-image-in-a-folder-using-python>
"""

import os


def get_latest_created_image(directory="./resources/", valid_extensions=['jpg', 'jpeg', 'png']):
    """
    Get the latest image valid_file in the given directory
    """
    # get valid_file paths of all files and dirs in the given dir
    valid_files = [os.path.join(directory, filename) for filename in os.listdir(directory)]
    # filter out directories, no-extension, and wrong extension files
    valid_files = [valid_file for valid_file in valid_files if '.' in
                   valid_file and valid_file.rsplit('.', 1)[-1] in valid_extensions and os.path.isfile(valid_file)]
    if not valid_files:
        raise ValueError("No valid images in %s" % directory)
    return max(valid_files, key=os.path.getctime)
