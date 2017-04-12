import cv2
import numpy as np

from functools import partial
from math import inf

from .contours import (PaintingFrameFinder,
                       filter_contours_with_predicates,
                       find_contour_with_lowest_point_distance_to_image_center,
                       is_xy_centroid_within_range,
                       is_area_size_within_range,
                       is_approximated_vertices_number_within_range,
                       compute_coordinates_center)
from .exceptions import VerticesNotFound
from .transformations import PerspectiveWarper, Figure
from .utils import StdErrOutputDisplayManager


class VerticesFinder:
    def __init__(self, filter_object, error_percentage=0.009, **kwargs):
        self.filter_object = filter_object
        self.error_percentage = error_percentage
        self.perspective_warper = kwargs.get('perspective_warper',
                                             PerspectiveWarper())
        self.painting_frame_finder = kwargs.get('painting_frame_finder',
                                                PaintingFrameFinder())

    def find_vertices(self, image):
        with StdErrOutputDisplayManager():
            try:
                return self._find_vertices(image)
            except cv2.error:
                raise VerticesNotFound('There was a problem when trying to '
                                       'find the vertices of the given image')

    def _find_vertices(self, image):
        frame_vertices = self.painting_frame_finder.find_frame_coordinates(image)
        warped_image = self.perspective_warper.change_image_perspective(
            image,
            frame_vertices
        )
        filtered_image = self.filter_object.filter_image(warped_image)
        return Figure(
            self._find_figure_vertices_from_filtered_image(filtered_image)
        )

    def _find_figure_vertices_from_filtered_image(self, filtered_image):
        _, contours, hierarchies = cv2.findContours(filtered_image,
                                                    cv2.RETR_TREE,
                                                    cv2.CHAIN_APPROX_SIMPLE)
        contours, hierarchies = filter_contours_with_predicates(
            contours,
            hierarchies,
            partial(is_area_size_within_range, minimum_size=3000),
            is_xy_centroid_within_range,
            is_approximated_vertices_number_within_range
        )

        contour = find_contour_with_lowest_point_distance_to_image_center(contours)
        epsilon = self.error_percentage * cv2.arcLength(contour, True)
        return cv2.approxPolyDP(contour, epsilon, True)


class HighFrequencyFilter:
    def __init__(self):
        pass

    def filter_image(self, image):
        blurred_image = cv2.bilateralFilter(image, 9, 75, 75)
        gray_image = cv2.cvtColor(blurred_image, cv2.COLOR_BGR2GRAY)

        gaussian_blurred_image = cv2.GaussianBlur(gray_image, (69, 69), 0)
        subtracted_image = cv2.subtract(gray_image, gaussian_blurred_image)
        equalized_image = cv2.equalizeHist(subtracted_image)
        _, thresholded_image = cv2.threshold(equalized_image, np.median(equalized_image), 255, 0)
        return thresholded_image


def find_best_figure(figures, *predicates, **kwargs):
    allowed_percentage = kwargs.get('allowed_percentage', 0.2)
    comparison_values = list(
        _compare_figures_with_predicates(figures, *predicates)
    )
    best_figure = None
    best_comparison_value = -inf
    best_figure_index = 0
    for index, (figure, comparison_value) in enumerate(zip(figures, comparison_values)):
        if best_comparison_value < comparison_value:
            best_figure, best_comparison_value, best_figure_index = figure, comparison_value, index
    if best_comparison_value < len(figures) * allowed_percentage:
        raise VerticesNotFound('No good figures could be found')
    return best_figure, best_figure_index


def _compare_figures_with_predicates(figures, *predicates):
    for figure_1 in figures:
        comparison_results = []
        for figure_2 in figures:
            try:
                comparison_results.append(
                    all(predicate(figure_1.coordinates, figure_2.coordinates)
                        for predicate in predicates)
                )
            except:
                comparison_results.append(False)
        yield sum(comparison_results)


def have_same_area_size(figure_1, figure_2, **kwargs) -> bool:
    lower_percentage = kwargs.get('lower_percentage', 0.05)
    upper_percentage = kwargs.get('upper_percentage', 1.05)
    same_area_size = False
    try:
        area_1 = cv2.contourArea(figure_1)
        area_2 = cv2.contourArea(figure_2)
        same_area_size = (lower_percentage * area_2 <=
                          area_1 <= upper_percentage * area_2)
    except cv2.error:
        pass
    return same_area_size


def have_same_perimeter_size(figure_1, figure_2, **kwargs) -> bool:
    lower_percentage = kwargs.get('lower_percentage', 0.05)
    upper_percentage = kwargs.get('upper_percentage', 1.05)
    same_perimeter_size = False
    try:
        perimeter_1 = cv2.arcLength(figure_1, True)
        perimeter_2 = cv2.arcLength(figure_2, True)
        same_perimeter_size = (lower_percentage * perimeter_2 <= perimeter_1 <=
                               upper_percentage * perimeter_2)
    except cv2.error:
        pass
    return same_perimeter_size


def have_same_center_position(figure_1, figure_2, **kwargs) -> bool:
    lower_percentage = kwargs.get('lower_percentage', 0.05)
    upper_percentage = kwargs.get('upper_percentage', 1.05)
    same_center = False
    try:
        x_1, y_1 = compute_coordinates_center(figure_1)
        x_2, y_2 = compute_coordinates_center(figure_2)
        same_center = (
            lower_percentage * x_2 <= x_1 <= upper_percentage * x_2 and
            lower_percentage * y_2 <= y_1 <= upper_percentage * y_2
        )
    except cv2.error:
        pass
    return same_center
