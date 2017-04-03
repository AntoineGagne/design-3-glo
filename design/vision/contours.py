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
    def __init__(self,
                 color_lower_range=PAINTING_FRAME_LOWER_GREEN,
                 color_upper_range=PAINTING_FRAME_UPPER_GREEN):
        self.color_lower_range = color_lower_range
        self.color_upper_range = color_upper_range

    def find_frame_coordinates(self, image):
        with StdErrOutputDisplayManager():
            try:
                return self._find_frame_coordinates(image)
            except cv2.error:
                raise PaintingFrameNotFound('There was an error while searching'
                                            'for the painting\'s frame '
                                            'coordinates.')

    def _find_frame_coordinates(self, image):
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
        blurred_image = cv2.GaussianBlur(image, (5, 5), 0)
        image_hsv = cv2.cvtColor(blurred_image, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(image_hsv,
                           self.color_lower_range,
                           self.color_upper_range)

        kernel = np.ones((9, 9), np.uint8)
        return cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)


def has_four_corners(contour, hierarchy) -> bool:
    vertices = []
    try:
        closed_contour = cv2.convexHull(contour)
        epsilon = 0.1 * cv2.arcLength(closed_contour, True)
        vertices = cv2.approxPolyDP(closed_contour, epsilon, True)
    except cv2.error:
        pass
    return len(vertices) == 4


def filter_contours_with_predicates(contours, hierarchies, *predicates):
    filtered_contours = []
    filtered_hierarchies = []
    for contour, hierarchy in zip(contours, chain.from_iterable(hierarchies)):
        if all(predicate(contour, hierarchy) for predicate in predicates):
            filtered_contours.append(contour)
            filtered_hierarchies.append(hierarchy)

    return filtered_contours, filtered_hierarchies


def is_area_size_within_range(contour, *args, **kwargs) -> bool:
    minimum_size = kwargs.get('minimum_size', 1000)
    maximum_size = kwargs.get('maximum_size', inf)
    return minimum_size < cv2.contourArea(contour) < maximum_size


def is_xy_centroid_within_range(contour, *args, **kwargs) -> bool:
    lower_bound = kwargs.get('lower_bound', 120)
    upper_bound = kwargs.get('upper_bound', 180)
    centroid_x, centroid_y = compute_coordinates_center(contour)
    return (lower_bound < centroid_x < upper_bound and
            lower_bound < centroid_y < upper_bound)


def is_approximated_vertices_number_within_range(contour, *args, **kwargs) -> bool:
    minimum_vertices_number = kwargs.get('minimum_vertices_number', 1)
    maximum_vertices_number = kwargs.get('maximum_vertices_number', 20)
    approximation_factor = kwargs.get('approximation_factor', 0.009)
    vertices = []
    try:
        epsilon = approximation_factor * cv2.arcLength(contour, True)
        vertices = cv2.approxPolyDP(contour, epsilon, True)
    except cv2.error:
        pass
    return minimum_vertices_number <= len(vertices) <= maximum_vertices_number


def find_contour_with_lowest_point_distance_to_image_center(contours, image_dimension=WARPED_IMAGE_DIMENSIONS):
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
    moment = cv2.moments(coordinates)
    centroid_x = 0
    centroid_y = 0
    try:
        centroid_x = coordinates_type(moment['m10'] / moment['m00'])
        centroid_y = coordinates_type(moment['m01'] / moment['m00'])
    except ZeroDivisionError:
        pass

    return centroid_x, centroid_y
