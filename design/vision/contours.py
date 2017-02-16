"""Module that contains functions related to contours."""
import cv2
import numpy as np

from .constants import (LOWER_GREEN,
                        UPPER_GREEN)


def find_green_square_coordinates(image):
    """Find the green square in the image.

    :param image: The image from which we want to extract the green square
    :returns: The coordinates of the four corners of the square
    """
    blurred_image = cv2.GaussianBlur(image, (5, 5), 0)
    image_hsv = cv2.cvtColor(blurred_image, cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(image_hsv.copy(), LOWER_GREEN, UPPER_GREEN)
    kernel = np.ones((9, 9), np.uint8)
    closed_mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    _, contours, hierarchy = cv2.findContours(closed_mask.copy(),
                                              cv2.RETR_TREE,
                                              cv2.CHAIN_APPROX_SIMPLE)
    # The hierarchies are in a matrix form so we remove them from the outer
    # list
    hierarchy = hierarchy[0]
    contour = find_innermost_contour_borders(contours, hierarchy)
    closed_contour = cv2.convexHull(contour)
    epsilon = 0.1 * cv2.arcLength(closed_contour, True)
    approximated_polygon = cv2.approxPolyDP(closed_contour, epsilon, True)

    return approximated_polygon


def find_innermost_contour_borders(contours, hierarchy):
    """Find the innermost contour by looking at the hierarchy and
       finding the one with a parent but no children.

    :param contours: The contours
    :param hierarchy: The hierarchy associated with those contours
    :returns: The corresponding contour or `None` if no such contour
             was found
    .. seealso:: For more informations about contour hierarchies, see
       http://docs.opencv.org/3.1.0/d9/d8b/tutorial_py_contours_hierarchy.html
    """
    found_contour = None
    for contour, contour_hierarchy in zip(contours, hierarchy):
        if contour_hierarchy[2] < 0:
            found_contour = contour
            break
    return found_contour
