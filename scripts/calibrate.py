#!/usr/bin/env python

"""Camera calibration for distorted images with chess board samples.
   reads distorted images, calculates the calibration and write undistorted
   images.

    .. note:: Edited from source code of OpenCV
"""
import cv2
import numpy as np

import os
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
from glob import glob
from errno import EEXIST


DEFAULT_IMAGES_DIRECTORY = './data/left*.jpg'
DEFAULT_OUTPUT_DIRECTORY = './output/'
CHESSBOARD_PATTERN_SIZE = (9, 6)


def parse_arguments():
    """Parse the command line arguments.

    :returns: The parsed arguments

    .. seealso::
        https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser.parse_args
    """
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter,
                            prog='calibrate',
                            description='Calibrate the camera.')
    parser.add_argument('-i',
                        '--input',
                        default=DEFAULT_IMAGES_DIRECTORY,
                        nargs='?',
                        type=str,
                        dest='input_directory',
                        help='Specify the directory from which to fetch the '
                             'images.')
    parser.add_argument('-o',
                        '--output',
                        default=DEFAULT_OUTPUT_DIRECTORY,
                        type=str,
                        nargs='?',
                        metavar='OUTPUT_DIRECTORY',
                        dest='output_directory',
                        help='Specify the directory where to output the '
                             'images.')
    parser.add_argument('-s',
                        default=True,
                        action='store_false',
                        dest='output',
                        help='Output the images.')
    return parser.parse_args()


def calibrate(directory=DEFAULT_IMAGES_DIRECTORY,
              output=True,
              output_directory=DEFAULT_OUTPUT_DIRECTORY):
    """Calibration

    :param directory: The directory that contains images
    :type directory: str
    :param output: if True, the images are
    :type output: bool
    :param output_directory: The directory that will contain original images
                             with found coordinates drawn
    :type output_directory: str
    :return: A tuple containing the root mean square and the intrinsic camera
             parameters
    :rtype: tuple
    """
    image_names = glob(directory)

    pattern_points = _prepare_pattern_points()

    # Arrays to store object points and image points from all the images.
    object_points = []  # 3d point in real world space
    image_points = []  # 2d points in image plane.

    height, width = 0, 0
    undistorted_image_names = []
    for filename in image_names:
        print('Processing {0}... -> '.format(filename), end='')
        image = cv2.imread(filename, 0)
        if image is None:
            print("Failed to load: {0}".format(filename))
            continue

        height, width = image.shape[:2]

        # Find the chess board corners
        found, corners = cv2.findChessboardCorners(image,
                                                   CHESSBOARD_PATTERN_SIZE)

        # If found, add object points, image points (after refining them)
        if found:
            term = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_COUNT, 30, 0.1)
            cv2.cornerSubPix(image, corners, (5, 5), (-1, -1), term)

        # we write the images with found coordinates
        if output:
            create_directory(output_directory)
            # We don't want a grayscale image to be displayed
            vis = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
            # Draw and display the corners
            cv2.drawChessboardCorners(vis,
                                      CHESSBOARD_PATTERN_SIZE,
                                      corners,
                                      found)
            # save the image to show where the corners are
            _, name, _ = split_filename(filename)
            output_file_name = '{0}{1}{2}'.format(output_directory,
                                                  name,
                                                  '_chess.png')
            cv2.imwrite(output_file_name, vis)
            if found:
                undistorted_image_names.append(output_file_name)

        if not found:
            print('The chessboard pattern could not be found.')
            continue

        image_points.append(corners.reshape(-1, 2))
        object_points.append(pattern_points)
        print('The processing was successful.')

    # root_mean_square: (RMS) reprojection error (should be between 0.1 and
    # 1.0 pixels in a good calibration)
    # camera_matrix: intrinsics parameters including focal length and optical
    # centers
    root_mean_square, camera_matrix, distorsion_coefficients, rotation_vectors, translation_vectors = \
        cv2.calibrateCamera(object_points, image_points, (width, height), None, None)
    return (root_mean_square,
            camera_matrix,
            distorsion_coefficients,
            rotation_vectors,
            translation_vectors)


def _prepare_pattern_points():
    """Prepare the pattern points.

    :returns: The pattern points
    """
    # We put cm values (but it can be 26 mm or 0.026 m)
    square_size = 2.6
    pattern_points = np.zeros((np.prod(CHESSBOARD_PATTERN_SIZE), 3), np.float32)
    pattern_points[:, :2] = np.indices(CHESSBOARD_PATTERN_SIZE).T.reshape(-1, 2)
    pattern_points *= square_size
    return pattern_points


def split_filename(filename):
    """Split the file's name.

    :param filename: The file's name
    :type filename: str
    :returns: A tuple containing the path, name and extension of the file
    :rtype: tuple<str, str, str>
    """
    path, filename = os.path.split(filename)
    name, extension = os.path.splitext(filename)
    return path, name, extension


def create_directory(path: str):
    """Create a directory at the given path if it doesn't exist.

    :param path: The path to the directory
    :type path: str
    """
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != EEXIST:
            raise


def get_onboard_extrinsic_vectors(image_number,
                                  rotation_vectors,
                                  translation_vectors):
    """Get a set of rotation and translation vectors for each image used to
       calibrate the camera. We set world coordinates origin based on the corner
       of the chessboard. Choosing the image allows to set the origin
       coordinates we will refer to afterwards.

    :param image_number: the image from which we want the referential
    :param rotation_vectors: rotation vectors obtained after calibration
    :param translation_vectors: translation vectors obtained after calibration
    :returns: single rotation and translation vectors
    """
    return rotation_vectors[image_number], translation_vectors[image_number]


def get_extrinsic_vectors(object_points,
                          image_points,
                          camera_matrix,
                          distorsion_coefficients,
                          rotation_vector=None,
                          translation_vector=None):
    """Get new rotation vector and translation vector values. Useful
       for new picture in which we know both image and world coordinates image
       points from vision.

    :param object_points:
    :param image_points:
    :param camera_matrix:
    :param distorsion_coefficients:
    :param rotation_vector: output parameter
    :param translation_vector: output parameter
    :returns:

    .. warning:: Careful for getting image points from undistorted image
                 or do not put the distorsion coefficients to bypass
                 undistorsion since it's already done.
    """
    value = not (rotation_vector is None and translation_vector is None)
    cv2.solvePnP(object_points,
                 image_points,
                 camera_matrix,
                 distorsion_coefficients,
                 rotation_vector,
                 translation_vector,
                 value)

    return rotation_vector, translation_vector


def calculate_extrinsic_matrix(rotation_matrix, translation_vector):
    """Get extrinsic matrix when we already have rotation and translation
       vectors.

    :param rotation_matrix: rotation vector
    :type rotation_matrix: :class:numpy.ndarray
    :param translation_vector: translation vector
    :type translation_vector: :class:numpy.ndarray
    :return: Extrinsic 3x4 matrix
    :rtype: :class:numpy.ndarray
    """
    matrix = np.zeros(shape=(3, 3))
    cv2.Rodrigues(rotation_matrix, matrix)
    return np.column_stack((rotation_matrix, translation_vector))


if __name__ == '__main__':
    arguments = parse_arguments()
    calibrate(arguments.input_directory,
              arguments.output,
              arguments.output_directory)
