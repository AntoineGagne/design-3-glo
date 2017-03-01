"""Module that contains functions related to contours."""
import cv2
import numpy as np
from scipy.spatial import distance

from itertools import chain, starmap
from math import inf
from operator import truediv
from typing import Tuple

from .constants import (PAINTING_FRAME_LOWER_GREEN,
                        PAINTING_FRAME_UPPER_GREEN,
                        WARPED_IMAGE_DIMENSIONS)
from .exceptions import PaintingFrameNotFound
from .utils import StdErrOutputDisplayManager


class PaintingFrameFinder:
    """An object that finds the green border around the paintings."""

    def __init__(self,
                 color_lower_range=PAINTING_FRAME_LOWER_GREEN,
                 color_upper_range=PAINTING_FRAME_UPPER_GREEN):
        """Initialize the :class:`design.vision.contours.PaintingBorderFinder`

        :param color_lower_range: The lower range of the painting's frame color
        :type color_lower_range: tuple<float, float, float>
        :param color_upper_range: The upper range of the painting's frame color
        :type color_upper_range: tuple<float, float, float>
        """
        self.color_lower_range = color_lower_range
        self.color_upper_range = color_upper_range

    def find_frame_coordinates(self, image):
        """Find the frame coordinates in the image.

        :param image: The image from which we want to extract the frame
        :returns: The coordinates of the four corners of the frame
        """
        with StdErrOutputDisplayManager():
            try:
                return self._find_frame_coordinates(image)
            except cv2.error:
                raise PaintingFrameNotFound('There was an error while searching'
                                            'for the painting\'s frame '
                                            'coordinates.')

    def _find_frame_coordinates(self, image):
        """Find the frame coordinates in the image.

        :param image: The image from which we want to extract the frame
        :returns: The coordinates of the four corners of the frame
        """
        mask = self._find_painting_frame_mask(image)
        _, contours, hierarchy = cv2.findContours(mask,

                                                  cv2.RETR_TREE,
                                                  cv2.CHAIN_APPROX_SIMPLE)
        contours, hierarchy = filter_contours_with_predicates(
            contours,
            hierarchy,
            is_area_size_within_range,
            has_four_corners
        )
        contour = find_contour_with_lowest_point_distance_to_image_center(
            contours,
            image.shape
        )
        closed_contour = cv2.convexHull(contour)
        epsilon = 0.1 * cv2.arcLength(closed_contour, True)

        return cv2.approxPolyDP(closed_contour, epsilon, True)

    def _find_painting_frame_mask(self, image):
        """Find the painting frame's mask.

        :param image: The image from which we want to extract the edges
        :returns: The green square mask
        """
        blurred_image = cv2.GaussianBlur(image, (5, 5), 0)
        image_hsv = cv2.cvtColor(blurred_image, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(image_hsv,
                           self.color_lower_range,
                           self.color_upper_range)

        kernel = np.ones((9, 9), np.uint8)
        return cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)


def has_four_corners(contour, hierarchy) -> bool:
    """Check if the contour has four corners.

    :param contour: The contour to check
    :param hierarchy: The hierarchy associated with the contour
    :returns: A boolean indicating if the contour has a parent
    :rtype: bool
    """
    vertices = []
    try:
        closed_contour = cv2.convexHull(contour)
        epsilon = 0.1 * cv2.arcLength(closed_contour, True)
        vertices = cv2.approxPolyDP(closed_contour, epsilon, True)
    except cv2.error:
        pass
    return len(vertices) == 4


def filter_contours_with_predicates(contours, hierarchies, *predicates):
    """Filter the contours with the given predicates.

    :param contours: The contours to filter
    :param hierarchies: The hierarchies of the contours
    :param predicates: The given predicate against which we want to filter the
                       contours
    :type predicates: tuple<function>
    :returns: A tuple containing the filtered contours and their hierarchies
    """
    filtered_contours = []
    filtered_hierarchies = []
    for contour, hierarchy in zip(contours, chain.from_iterable(hierarchies)):
        if all(predicate(contour, hierarchy) for predicate in predicates):
            filtered_contours.append(contour)
            filtered_hierarchies.append(hierarchy)

    return filtered_contours, filtered_hierarchies


def is_area_size_within_range(contour, *args, **kwargs) -> bool:
    """Check if the given contour is within a size range.

    :param contour: The contour to check
    :param kwargs: See below
    :returns: A boolean indicating if the contour respects the boundaries
    :rtype: bool

    :Keyword Arguments:
        * *minimum_size* (``float``) -- The lower bound of the area size
        * *maximum_size* (``float``) -- The upper bound of the area size
    """
    minimum_size = kwargs.get('minimum_size', 1000)
    maximum_size = kwargs.get('maximum_size', inf)
    return minimum_size < cv2.contourArea(contour) < maximum_size


def is_xy_centroid_within_range(contour, *args, **kwargs) -> bool:
    """Check if the centroid is within the range specified for the xy coordinates.

    :param contour: The contour to check
    :param kwargs: See below
    :returns: A boolean indicating if the contour's centroids respect the
              boundaries
    :rtype: bool

    :Keyword Arguments:
        * *lower_bound* (``float``) -- The lower bound of the centroids
        * *upper_bound* (``float``) -- The upper bound of the centroids

    .. seealso:
       http://docs.opencv.org/3.1.0/dd/d49/tutorial_py_contour_features.html
    """
    lower_bound = kwargs.get('lower_bound', 120)
    upper_bound = kwargs.get('upper_bound', 180)
    centroid_x, centroid_y = compute_coordinates_center(contour)
    return (lower_bound < centroid_x < upper_bound and
            lower_bound < centroid_y < upper_bound)


def find_contour_with_lowest_point_distance_to_image_center(contours, image_dimension=WARPED_IMAGE_DIMENSIONS):
    """Find the contour with the lowest average distance to the image center.

    :param contours: The contours to check
    :param image_dimension: The dimension of the image
    :type image_dimension: tuple or list
    :returns: The given contour or ``None``
    """
    image_center = list(starmap(truediv, zip(image_dimension, (2, 2))))
    image_center_position = np.array([image_center])
    right_contour = None
    right_contour_mean = inf
    for contour in contours:
        average_distance = distance.cdist(
            np.array(list(chain.from_iterable(contour))),
            image_center_position
        ).mean()
        if average_distance < right_contour_mean:
            right_contour_mean = average_distance
            right_contour = contour

    return right_contour


def compute_coordinates_center(coordinates: np.ndarray,
                               coordinates_type=int) -> Tuple[int, int]:
    """Find the xy coordinates of the given points.

    :param coordinates: The coordinates from which we want to find the center
    :type coordinates: :class:`numpy.ndarray`
    :param coordinates_type: The format of the coordinates (float or int)
    :type coordinates_type: function
    :returns: A tuple containing the xy coordinates of the center
    :rtype: tuple<int, int>
    """
    moment = cv2.moments(coordinates)
    centroid_x = coordinates_type(moment['m10'] / moment['m00'])
    centroid_y = coordinates_type(moment['m01'] / moment['m00'])

    return centroid_x, centroid_y
