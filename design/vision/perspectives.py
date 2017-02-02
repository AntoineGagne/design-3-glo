"""Modules that contains functions related to perspectives changes"""
import cv2
import numpy as np

from .constants import (WARPED_IMAGE_CORNERS,
                        WARPED_IMAGE_DIMENSIONS)
from .utils import order_points


def change_image_perspective(image, source_points):
    """Change the image perspective so that it is at 0° angle and in 2D.

    :param image: The image whose perspective is to be changed
    :param source_points: The detected points of the green rectangle
    :returns: The image with its perspective changed
    """
    # The points may not be in the right order and the right format
    # We convert it to the format expected by `warpPerspective`
    source_points = np.array(order_points(source_points),
                             dtype='float32')
    reference_points = np.array(WARPED_IMAGE_CORNERS)
    transformation_matrix, _ = cv2.findHomography(source_points,
                                                  reference_points)
    return cv2.warpPerspective(image,
                               transformation_matrix,
                               WARPED_IMAGE_DIMENSIONS)
