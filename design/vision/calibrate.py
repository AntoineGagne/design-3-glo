#!/usr/bin/env python

'''
camera calibration for distorted images with chess board samples
reads distorted images, calculates the calibration and write undistorted images
Code edited from source code of OpenCV
'''

import numpy as np
import cv2
import os
from glob import glob


def split_filename(filename):
    path, filename = os.path.split(filename)
    name, extension = os.path.splitext(filename)
    return path, name, extension


def calibrate(directory='', output=1, output_directory=''):
    """
    Function used for calibration
    :param directory: The directory that contains images
    :type directory: str
    :param output: if 1 (true), the images are
    :type output: bool
    :param output_directory: The directory that will contain original images with found coordinates drawn
    :type output_directory: str
    :return: root_mean_square : root mean square, camera_matrix : intrinsic camera parameters,
    dist_coefs : distorsion coefficients, rotation_vectors : rotation vectors for each image,
    translation_vectors : translation vectors for each image
    :type: tuple
    """
    if directory == '':
        directory = './data/left*.jpg'
    image_names = glob(directory)

    square_size = float(2.6)  # we put cm values (but can be 26 mm or 0.026 m)

    # this is the pattern chessboard we found on OpenCV tutorials
    pattern_size = (9, 6)
    # 3x3 matrix
    # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
    pattern_points = np.zeros((np.prod(pattern_size), 3), np.float32)
    pattern_points[:, :2] = np.indices(pattern_size).T.reshape(-1, 2)
    pattern_points *= square_size

    # Arrays to store object points and image points from all the images.
    object_points = []  # 3d point in real world space
    image_points = []  # 2d points in image plane.

    height, width = 0, 0
    img_names_undistort = []
    for fn in image_names:
        print('processing %s... ' % fn, end='')
        image = cv2.imread(fn, 0)
        if image is None:
            print("Failed to load", fn)
            continue

        height, width = image.shape[:2]

        # Find the chess board corners
        found, corners = cv2.findChessboardCorners(image, pattern_size)

        # If found, add object points, image points (after refining them)
        if found:
            term = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_COUNT, 30, 0.1)
            cv2.cornerSubPix(image, corners, (5, 5), (-1, -1), term)

        # we write the images with found coordinates
        if output:
            if output_directory == '':
                output_directory = './output/'
            if not os.path.isdir(output_directory):
                os.mkdir(output_directory)

            # We don't want a grayscale image to be displayed
            vis = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
            # Draw and display the corners
            cv2.drawChessboardCorners(vis, pattern_size, corners, found)
            # save the image to show where the corners are
            path, name, ext = split_filename(fn)
            outfile = output_directory + name + '_chess.png'
            cv2.imwrite(outfile, vis)
            if found:
                img_names_undistort.append(outfile)

        if not found:
            print('chessboard not found')
            continue

        image_points.append(corners.reshape(-1, 2))
        object_points.append(pattern_points)
        print('ok')

    # calculate camera parameters
    # root_mean_square : (RMS) reprojection error (should be between 0.1 and 1.0 pixels in a good calibration)
    # camera_matrix : intrinsics parameters including focal length and optical centers
    root_mean_square, camera_matrix, distorsion_coefficients, rotation_vectors, translation_vectors = \
        cv2.calibrateCamera(object_points, image_points, (width, height), None, None)
    return root_mean_square, camera_matrix, distorsion_coefficients, rotation_vectors, translation_vectors


def get_onboard_extrinsic_vectors(image_number, rotation_vectors, translation_vectors):
    """
    We get a set of rotation and translation vectors for each image used
    to calibrate the camera. We set world coordinates origin based on
    the corner of the chessboard. Choosing the image allows to set
    the origin coordinates we will refer to afterwards
    :param image_number: the image from which we want the referential
    :param rotation_vectors: rotation vectors obtained after calibration
    :param translation_vectors: translation vectors obtained after calibration
    :return: single rotation and translation vectors
    """
    return rotation_vectors[image_number], translation_vectors[image_number]


# useful for new picture taken in which we know both image and world coordinates
# image points from vision : careful for getting image pts from undistorted image
# or do not put the distorsion coefficients to bypass undistorsion since it's already done
def get_extrinsic_vectors(object_points, image_points, camera_matrix, distorsion_coefficients, rotation_vector=None,
                          translation_vector=None):
    """
    Function to get new rvec and tvec values
    useful for new picture taken in which we know both image and world coordinates
    image points from vision : careful for getting image pts from undistorted image
    or do not put the distorsion coefficients to bypass undistorsion since it's already done
    :param object_points:
    :param image_points:
    :param camera_matrix:
    :param distorsion_coefficients:
    :param rotation_vector: output parameter
    :param translation_vector: output parameter
    :return:
    """
    if rotation_vector is None and translation_vector is None:
        cv2.solvePnP(object_points, image_points, camera_matrix, distorsion_coefficients, rotation_vector,
                     translation_vector, 0)
    else:
        cv2.solvePnP(object_points, image_points, camera_matrix, distorsion_coefficients, rotation_vector,
                     translation_vector, 1)
    return rotation_vector, translation_vector


def calculate_extrinsic_matrix(rotation_matrix, translation_vector):
    """
    Function to get extrinsic matrix when we already have rotation and translation vectors
    :param rotation_matrix: rotation vector
    :type rotation_matrix: array
    :param translation_vector: translation vector
    :type translation_vector: array
    :return: extrinsic 3x4 matrix
    :type: numpy.array
    """
    matrix = np.zeros(shape=(3, 3))
    cv2.Rodrigues(rotation_matrix, matrix)
    return np.column_stack((rotation_matrix, translation_vector))
