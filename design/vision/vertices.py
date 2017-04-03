import cv2
import numpy as np

from functools import partial

from .contours import (PaintingFrameFinder,
                       filter_contours_with_predicates,
                       find_contour_with_lowest_point_distance_to_image_center,
                       is_xy_centroid_within_range,
                       is_area_size_within_range,
                       is_approximated_vertices_number_within_range)
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
