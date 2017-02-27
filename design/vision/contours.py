"""Module that contains functions related to contours."""
import cv2
import numpy as np
from scipy.spatial import distance

from itertools import chain, starmap
from math import inf
from operator import truediv
from typing import Tuple, List, Callable, Any

from design.vision.constants import (PAINTING_FRAME_LOWER_GREEN,
                                     PAINTING_FRAME_UPPER_GREEN,
                                     WARPED_IMAGE_DIMENSIONS)


class PaintingBorderFinder:
    """An object that finds the green border around the paintings."""

    @staticmethod
    def find_green_square_coordinates(image):
        """Find the green square in the image.

        :param image: The image from which we want to extract the green square
        :returns: The coordinates of the four corners of the square
        """
        edges = _find_green_square_edges(image)
        _, contours, hierarchy = cv2.findContours(edges,
                                                  cv2.RETR_TREE,
                                                  cv2.CHAIN_APPROX_SIMPLE)
        contours, hierarchy = filter_contours_with_predicates(
            contours,
            hierarchy,
            is_area_size_within_range,
            has_no_child_contour
        )
        contour = find_contour_with_lowest_point_distance_to_image_center(contours, image.shape)
        closed_contour = cv2.convexHull(contour)
        epsilon = 0.1 * cv2.arcLength(closed_contour, True)

        return cv2.approxPolyDP(closed_contour, epsilon, True)


def _find_green_square_edges(image):
    """Find the green square edges.

    :param image: The image from which we want to extract the edges
    :returns: The green square edges
    """
    blurred_image = cv2.GaussianBlur(image, (5, 5), 0)
    image_hsv = cv2.cvtColor(blurred_image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(image_hsv, PAINTING_FRAME_LOWER_GREEN, PAINTING_FRAME_UPPER_GREEN)

    kernel = np.ones((9, 9), np.uint8)
    closed_mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    return cv2.Canny(closed_mask, 200, 200)


def has_no_child_contour(contour, hierarchy):
    """Check if the given contour has no child contour.

    :param contour: The contour to check
    :param hierarchy: The hierarchy associated with the contour
    :returns: A boolean indicating if the contour has a parent
    :rtype: bool
    """
    return hierarchy[2] < 0


def filter_contours_with_predicates(contours, hierarchies, *predicates):
    """Filter the contours with the given predicates.

    :param contours: The contours to filter
    :param hierarchies: The hierarchies of the contours
    :param *predicates: The given predicate against which we want to filter the
                        contours
    :type *predicates: tuple<function>
    :returns: A tuple containing the filtered contours and their hierarchies
    """
    filtered_contours = []
    filtered_hierarchies = []
    for contour, hierarchy in zip(contours, chain.from_iterable(hierarchies)):
        if all(predicate(contour, hierarchy) for predicate in predicates):
            filtered_contours.append(contour)
            filtered_hierarchies.append(hierarchy)

    return filtered_contours, filtered_hierarchies


def is_area_size_within_range(contour, *args, **kwargs):
    """Check if the given contour is within a size range.

    :param contour: The contour to check
    :param kwargs: See below
    :returns: A boolean indicating if the contour respects the boundaries
    :rtype: bool

    :Keyword Arguments:
        * *minimum_size* (``float``) -- The lower bound of the area size
        * *maximum_size* (``float``) -- The upper bound of the area size
    """
    minimum_size = kwargs.get('minimum_size', 800)
    maximum_size = kwargs.get('maximum_size', inf)
    return minimum_size < cv2.contourArea(contour) < maximum_size


def is_xy_centroid_within_range(contour, *args, **kwargs):
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


def find_best_match_contour(contours: List[Any]) -> Tuple[Any, float]:
    """Find the contours that has the most similarities with the other contours.

    :param contours: The contours to compare
    :type contours: list<:mod:transformations.Figure>
    :returns: The figure with the lowest coefficient along with its coefficient
    :rtype: tuple<:mod:transformations.Figure, float>
    """
    match_coefficients = []
    for contour in contours:
        match_coefficients.append(sum(map(_find_match_coefficient(contour), contours)) / len(contours))

    best_contour = (None, inf)
    for index, coefficient in enumerate(match_coefficients):
        if best_contour[1] > coefficient:
            best_contour = contours[index], coefficient

    return best_contour


def _find_match_coefficient(contour: Any, upper_bound: float=1, lower_bound: float=0.0) -> Callable:
    """Compare two contours with each other.

    :param contour: The first contour to compare
    :type contour: :mod:transformations.Figure
    :param upper_bound: The upper bound of the coefficient
    :type upper_bound: int
    :param lower_bound: The lower bound of the coefficient
    :type lower_bound: float
    :returns: A function that can be called with the second contour to be
              compared
    :rtype: function
    """
    def function_wrapper(contour_2: Any) -> float:
        """A closure that compare the outer scope contour with its argument.

        :param contour_2: The second contour to compare
        :type contour_2: :mod:transformations.Figure
        :returns: The coefficient of similarity
        :rtype: float
        """
        return cv2.matchShapes(contour.coordinates, contour_2.coordinates, upper_bound, lower_bound)

    return function_wrapper


def close_edges(edges, kernel_dimension=(5, 5)):
    """Morph the edges so that the gaps are closed.

    :param edges: The edges to morph
    :param kernel_dimension: The dimension of the kernel to use in the
                             morphological transformation
    :type kernel_dimension: tuple<int, int>
    :returns: The morphed edges
    """
    kernel = np.ones(kernel_dimension, np.uint8)
    closed_edges = cv2.morphologyEx(edges, cv2.MORPH_GRADIENT, kernel)
    return cv2.morphologyEx(closed_edges, cv2.MORPH_CLOSE, kernel)


def compute_coordinates_center(coordinates: np.ndarray, coordinates_type=int) -> Tuple[int, int]:
    """Find the xy coordinates of the given points.

    :param coordinates: The coordinates from which we want to find the center
    :type coordinates: :mod:`numpy`.`ndarray`
    :param coordinates_type: The format of the coordinates (float or int)
    :type coordinates_type: function
    :returns: A tuple containing the xy coordinates of the center
    :rtype: tuple<int, int>
    """
    moment = cv2.moments(coordinates)
    centroid_x = coordinates_type(moment['m10'] / moment['m00'])
    centroid_y = coordinates_type(moment['m01'] / moment['m00'])

    return centroid_x, centroid_y
