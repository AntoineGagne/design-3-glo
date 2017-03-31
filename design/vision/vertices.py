"""Contains the classes and functions related to contours filtering."""

import cv2

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
    """Find the vertices with filter operations."""

    def __init__(self, filter_object, error_percentage=0.009, **kwargs):
        """Initialize the object.

        :param filter_object: An object that has a filtering operation
        :param error_percentage: The error percentage of `approxPolyDP`
                                 (default: 0.009)
        :type error_percentage: float
        :param kwargs: See below

        :Keyword Arguments:
            * perspective_warper (:class:`design.vision.transformations.PerspectiveWarper`): Object that contains the
                                                                                             method used to warp an image perspective
            * painting_frame_finder (:class:`design.vision.contours.PaintingFrameFinder`): Object that finds the painting's
                                                                                           frame coordinates
        """
        self.filter_object = filter_object
        self.error_percentage = error_percentage
        self.perspective_warper = kwargs.get('perspective_warper',
                                             PerspectiveWarper())
        self.painting_frame_finder = kwargs.get('painting_frame_finder',
                                                PaintingFrameFinder())

    def find_vertices(self, image):
        """Find the vertices of the geometric shape within the given image.

        :param image: The image in which we want to find the geometric figure
        :returns: The vertices of the geometric figure

        :raises :class:`design.vision.exceptions.VerticesNotFound`: If the vertices could not be found.
        """
        with StdErrOutputDisplayManager():
            try:
                return self._find_vertices(image)
            except cv2.error:
                raise VerticesNotFound('There was a problem when trying to '
                                       'find the vertices of the given image')

    def _find_vertices(self, image):
        """Find the vertices of the geometric shape within the given image.

        :param image: The image in which we want to find the geometric figure
        :returns: The vertices of the geometric figure
        """
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
        """Find the vertices of the geometrical figure from the given edges.

        :param filtered_image: The filtered image from which to find the figure's
                               vertices
        :returns: The figure's vertices
        """
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
    """A high frequency filter"""

    def __init__(self):
        """Initialize the filter."""
        pass

    def filter_image(self, image):
        """Filter the geometric figure in the image by using
           high frequency filter.

        :param image: The image from which we want to extract the vertices
        :returns: The filtered image
        """
        blurred_image = cv2.bilateralFilter(image, 9, 75, 75)
        gray_image = cv2.cvtColor(blurred_image, cv2.COLOR_BGR2GRAY)

        gaussian_blurred_image = cv2.GaussianBlur(gray_image, (69, 69), 0)
        subtracted_image = cv2.subtract(gray_image, gaussian_blurred_image)
        cv2.normalize(subtracted_image,
                      subtracted_image,
                      0, 255,
                      cv2.NORM_MINMAX)
        _, thresholded_image = cv2.threshold(subtracted_image, 0, 255, 0)
        return thresholded_image
