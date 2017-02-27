"""Contains the classes and functions related to contours filtering."""

import cv2
import numpy as np

from design.vision.constants import (LOWER_WHITE,
                                     UPPER_WHITE)
from design.vision.contours import (PaintingBorderFinder,
                                    filter_contours_with_predicates,
                                    find_best_match_contour,
                                    find_contour_with_lowest_point_distance_to_image_center,
                                    is_xy_centroid_within_range,
                                    is_area_size_within_range)
from design.vision.transformations import PerspectiveWarper, Figure
from design.vision.utils import identity, StdErrOutputDisplayManager


def find_geometric_figure_vertices(image, *vertices_finders):
    """Call multiple functions to find vertices.

    :param image: The image from which we want to extract the vertices
    :returns: The vertices
    """
    vertices = []
    with StdErrOutputDisplayManager():
        for vertices_finder in vertices_finders:
            try:
                vertices.append(vertices_finder.find_vertices(image))
            except cv2.error:
                continue
    vertices, _ = find_best_match_contour(vertices)
    return vertices


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
            * perspective_warper (`PerspectiveWarper`): Object that contains the method used to warp an image perspective
        """
        self.filter_object = filter_object
        self.error_percentage = error_percentage
        self.perspective_warper = kwargs.get('perspective_warper', PerspectiveWarper())

    def find_vertices(self, image):
        """Find the vertices of the geometric shape within the given image.

        :param image: The image in which we want to find the geometric figure
        :returns: The vertices of the geometric figure
        """
        green_squares_vertices = PaintingBorderFinder.find_green_square_coordinates(image)
        warped_image = self.perspective_warper.change_image_perspective(image, green_squares_vertices)
        filtered_image = self.filter_object.filter_image(warped_image)
        return Figure(self._find_figure_vertices_from_filtered_image(filtered_image))

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
            is_area_size_within_range,
            is_xy_centroid_within_range
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
        cv2.normalize(subtracted_image, subtracted_image, 0, 255, cv2.NORM_MINMAX)
        _, thresholded_image = cv2.threshold(subtracted_image, 15, 255, 0)
        return thresholded_image


class AdaptiveThresholdingFilter:
    """An adaptive thresholding filter"""

    def __init__(self, morphological_operation=identity):
        """Initialize the filter.

        :param morphological_operation: The morphological operation to perform
                                        on the edges
        :type morphological_operation: function
        """
        self.morphological_operation = morphological_operation

    def filter_image(self, image):
        """Filter the geometric figure in the image by using
           adaptive thresholding.

        :param image: The image from which we want to extract the vertices
        :returns: The filtered image
        """
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        thresholded_image = cv2.adaptiveThreshold(gray_image, 255,
                                                  cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                                  cv2.THRESH_BINARY, 11, 2)
        edges = _find_figure_edges(thresholded_image)
        return self.morphological_operation(edges)


class HsvColorspaceFilter:
    """A HSV colorspace filter"""

    def __init__(self, morphological_operation=identity):
        """Initialize the filter.

        :param morphological_operation: The morphological operation to perform
                                        on the edges
        :type morphological_operation: function
        """
        self.morphological_operation = morphological_operation

    def filter_image(self, image):
        """Filter the geometric figure in the image by using
           HSV colorspace.

        :param image: The image from which we want to extract the vertices
        :returns: The filtered image
        """
        image_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        edges = _find_figure_edges(image_hsv)
        return self.morphological_operation(edges)


class WhiteBackgroundFilter:
    """A white background filter"""

    def __init__(self):
        """Initialize the filter."""
        pass

    def filter_image(self, image):
        """Filter the geometric figure in the image by using white color
           filter.

        :param image: The image from which we want to extract the vertices
        :returns: The filtered image
        """
        image_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        blurred_image = cv2.bilateralFilter(image_hsv, 9, 75, 75)
        mask = cv2.inRange(blurred_image, LOWER_WHITE, UPPER_WHITE)
        return cv2.bitwise_not(mask)


class LaplacianFilter:
    """A Laplacian filter"""

    def __init__(self):
        """Initialize the filter."""
        pass

    def filter_image(self, image):
        """Filter the geometric figure in the image by using Laplacian
           filtering.

        :param image: The image from which we want to extract the figure
        :returns: The filtered image
        """
        blurred_image = cv2.bilateralFilter(image, 5, 75, 75)
        gray_image = cv2.cvtColor(blurred_image, cv2.COLOR_BGR2GRAY)

        laplacian = cv2.Laplacian(gray_image, cv2.CV_32F, gray_image)
        blurred_image = cv2.bilateralFilter(laplacian, 9, 75, 75)
        _, thresholded_image = cv2.threshold(blurred_image,
                                             0.1, 255, 0)
        thresholded_image = np.absolute(thresholded_image)
        thresholded_image = np.uint8(thresholded_image)

        return thresholded_image


class OtsuBinarizationFilter:
    """A filter using Otsu's binarization"""

    def __init__(self):
        """Initialize the filter."""
        pass

    def filter_image(self, image):
        """Filter the geometric figure in the image by using Otsu's binarization.

        :param image: The image from which we want to extract the figure
        :returns: The filtered image
        """
        blurred_image = cv2.bilateralFilter(image, 5, 75, 75)
        gray_image = cv2.cvtColor(blurred_image, cv2.COLOR_BGR2GRAY)

        _, thresholded_image = cv2.threshold(gray_image, 0, 255,
                                             cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        thresholded_image = np.absolute(thresholded_image)
        thresholded_image = np.uint8(thresholded_image)
        return thresholded_image


def _find_figure_edges(image):
    """Find the edges in the given image.

    :param image: The image from which we want to find the edges
    :returns: The edges of the image
    """
    kernel = np.ones((3, 3), np.uint8)
    closed_image = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
    edges = cv2.Canny(closed_image, 200, 200)
    return edges
