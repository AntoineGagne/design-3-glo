#!/usr/bin/env python

"""Camera calibration for distorted images with chess board samples.
   reads distorted images, calculates the calibration and write undistorted
   images.

    .. note:: Edited from source code of OpenCV
"""
import cv2
import numpy as np
import json
import os
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
from glob import glob
from errno import EEXIST

DEFAULT_IMAGES_DIRECTORY = './data/*.png'
DEFAULT_OUTPUT_DIRECTORY = './output/'
CHESSBOARD_PATTERN_SIZE = (9, 6)
CHESSBOARD_SQUARE_SIZE = 4.3  # in cm
DEFAULT_TABLE_NUMBER = 1


def parse_arguments():
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
    parser.add_argument('-t',
                        '--table',
                        default=DEFAULT_TABLE_NUMBER,
                        type=int,
                        dest='table_number',
                        help='Table number to calibrate.')
    return parser.parse_args()


def calibrate(directory=DEFAULT_IMAGES_DIRECTORY,
              output=True,
              output_directory=DEFAULT_OUTPUT_DIRECTORY):
    """Calibration

    :param directory: The directory that contains images
    :type directory: str
    :param output: if True, the images are saved to output directory
    :type output: bool
    :param output_directory: The directory that will contain original images
                             with found coordinates drawn
    :type output_directory: str
    :return: A tuple containing the root mean square and the camera parameters
    :rtype: tuple
    """
    image_names = glob(directory)

    pattern_points = _prepare_pattern_points()

    # Arrays to store object points and image points from all the images.
    object_points = []  # 3d point in real world space
    image_points = []  # 2d points in image plane.

    height, width = 0, 0
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
        if not found:
            print('The chessboard pattern could not be found.')
            continue

        image_points.append(corners.reshape(-1, 2))
        object_points.append(pattern_points)
        print('The processing was successful.')

    # root_mean_square: (RMS) reprojection error (should be between 0.1 and 1.0 pixels in a good calibration)
    # camera_matrix: intrinsics parameters including focal length and optical centers
    root_mean_square, camera_matrix, distorsion_coefficients, rotation_vectors, translation_vectors = \
        cv2.calibrateCamera(object_points, image_points, (width, height), None, None)

    return (root_mean_square,
            camera_matrix,
            distorsion_coefficients,
            rotation_vectors,
            translation_vectors)


def _prepare_pattern_points():
    pattern_points = np.zeros((np.prod(CHESSBOARD_PATTERN_SIZE), 3), np.float32)
    pattern_points[:, :2] = np.indices(CHESSBOARD_PATTERN_SIZE).T.reshape(-1, 2)
    pattern_points *= CHESSBOARD_SQUARE_SIZE
    return pattern_points


def split_filename(filename):
    path, filename = os.path.split(filename)
    name, extension = os.path.splitext(filename)
    return path, name, extension


def create_directory(path: str):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != EEXIST:
            raise


def write_json_file(table_number, intrinsic_matrix, rotation_vector, translation_vector):
    calibration_data = {"intrinsic_matrix": intrinsic_matrix,
                        "rotation_vector": rotation_vector,
                        "translation_vector": translation_vector}
    data_file_name = 'calibration_information_{}.json'.format(table_number)
    with open(data_file_name, 'w', encoding='utf-8') as output_file:
        json.dump(calibration_data, output_file)


if __name__ == '__main__':
    rms, matrix_camera, _, rotation_vectors, translation_vectors = calibrate(
        './camera_data4/photo*.png')
    print("The root mean square is {}\nIt should be between 0.1 and 1.0 pixels in a good calibration".format(rms))
    write_json_file(4,
                    matrix_camera.tolist(),
                    rotation_vectors[0].tolist(),
                    translation_vectors[0].tolist())
