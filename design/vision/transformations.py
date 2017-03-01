"""Modules that contains functions related to perspectives changes"""
import math
from functools import partial, reduce

import cv2
import numpy as np

from .contours import compute_coordinates_center
from .constants import (WARPED_IMAGE_DIMENSIONS,
                        WARPED_IMAGE_CORNERS)
from .utils import order_points


class PerspectiveWarper:
    """An object to warp an image perspective."""

    def __init__(self,
                 destination_points=WARPED_IMAGE_CORNERS,
                 image_dimensions=WARPED_IMAGE_DIMENSIONS):
        """Initialize the `PerspectiveWarper`.

        :param destination_points: The destination point to warp to
        :param image_dimensions: The image's dimensions after the warping
        """
        self.destination_points = destination_points
        self.image_dimensions = image_dimensions

    def change_image_perspective(self, image, source_points):
        """Change the image perspective so that it is at 0° angle and in 2D.

        :param image: The image whose perspective is to be changed
        :param source_points: The detected points to warp from
        :returns: The image with its perspective changed
        """
        # The points may not be in the right order and the right format
        # We convert it to the format expected by `warpPerspective`
        source_points = np.array(order_points(source_points),
                                 dtype='float32')
        reference_points = np.array(self.destination_points)
        transformation_matrix, _ = cv2.findHomography(source_points,
                                                      reference_points)
        return cv2.warpPerspective(image,
                                   transformation_matrix,
                                   self.image_dimensions)


class Figure:
    """Contain figure's coordinates and allow transformations over them."""

    def __init__(self, coordinates: np.ndarray):
        """Initialize the figure.

        :param coordinates: The figure's coordinates
        :type coordinates: :class:`numpy.ndarray`
        """
        self._homogeneous_coordinates = convert_to_homogeneous_coordinates(coordinates)
        self._coordinates = coordinates

    @property
    def coordinates(self) -> np.ndarray:
        """Getter for the coordinates.

        :returns: The transformed coordinates
        :rtype: :class:`numpy.ndarray`
        """
        return self._coordinates

    @coordinates.setter
    def coordinates(self, coordinates: np.ndarray):
        """Setter for the coordinates.

        :param coordinates: The figure's coordinates
        :type coordinates: :class:`numpy.ndarray`
        """
        self._coordinates = coordinates
        self._homogeneous_coordinates = convert_to_homogeneous_coordinates(
            coordinates
        )

    def apply_transformations(self, *transformations) -> 'Figure':
        """Apply the given transformations to the figure.

        :param transformations: The transformations to be applied in order
        :type transformations: tuple<Any>
        :returns: The transformed figure
        :rtype: :class:design.vision.transformations.Figure
        """
        return Figure(
            convert_to_cartesian_coordinates(
                reduce(
                    lambda coordinates, transformation: transformation.apply(coordinates),
                    transformations,
                    self._homogeneous_coordinates
                )
            )
        )


class ScaleTransformation:
    """Apply scale transformation on coordinates."""

    def __init__(self, x: float, y: float=None):
        """Initialize the transformation object

        :param x: The scaling on the x axis
        :type x: float
        :param y: The scaling on the y axis (default: None)
        :type y: float

        .. note:: If the *y* parameter is None, then it has the same value as
                  the *x* parameter.
        """
        self.x = x
        self.y = y if y else x

    def apply(self, homogeneous_coordinates: np.ndarray) -> np.ndarray:
        """Apply the transformation to the given coordinates.

        :param homogeneous_coordinates: The coordinates to scale
        :type homogeneous_coordinates: :class:`numpy.ndarray`
        :returns: The scaled coordinates
        :rtype: :class:`numpy.ndarray`
        """
        return self._scale(homogeneous_coordinates)

    def _scale(self, homogeneous_coordinates: np.ndarray) -> np.ndarray:
        """Scale the coordinates by the specified xy factor.

        :param homogeneous_coordinates: The coordinates to scale
        :type homogeneous_coordinates: :class:`numpy.ndarray`
        :returns: The transformed coordinates
        :rtype: :class:`numpy.ndarray`
        """
        previous_homogeneous_coordinates = homogeneous_coordinates.copy()
        scaling_matrix = np.array([[self.x, 0, 0],
                                   [0, self.y, 0],
                                   [0, 0, 1]])

        scale_point = partial(_apply_transformation_matrix_on_point, scaling_matrix)
        homogeneous_coordinates = np.apply_along_axis(scale_point, 2, previous_homogeneous_coordinates)

        x, y = _find_xy_center_deviation(homogeneous_coordinates, previous_homogeneous_coordinates)
        translate_transformation = TranslateTransformation(x, y)
        return translate_transformation.apply(homogeneous_coordinates)


def _find_xy_center_deviation(homogeneous_coordinates: np.ndarray,
                              previous_homogeneous_coordinates: np.ndarray) -> np.ndarray:
    """Find the deviation between the previous coordinates and the current
       ones.

    :param previous_homogeneous_coordinates: The previous coordinates
    :type previous_homogeneous_coordinates: :class:`numpy.ndarray`
    :returns: The xy values of the deviation
    :rtype: :class:`numpy.ndarray`
    """
    center = compute_coordinates_center(
        convert_to_cartesian_coordinates(homogeneous_coordinates),
        float
    )
    previous_center = compute_coordinates_center(
        convert_to_cartesian_coordinates(previous_homogeneous_coordinates),
        float
    )
    return np.subtract(previous_center, center)


class TranslateTransformation:
    """Apply translation transformation on coordinates"""

    def __init__(self, x: float, y: float):
        """Initialize the transformation.

        :param x: The x translation value
        :type x: float
        :param y: The y translation value
        :type y: float
        """
        self.x = x
        self.y = y

    def apply(self, homogeneous_coordinates: np.ndarray) -> np.ndarray:
        """Apply the translation to the given coordinates.

        :param homogeneous_coordinates: The coordinates to translate
        :type homogeneous_coordinates: :class:`numpy.ndarray`
        :returns: The translated coordinates
        :rtype: :class:`numpy.ndarray`
        """
        return self._translate(homogeneous_coordinates)

    def _translate(self, homogeneous_coordinates: np.ndarray) -> np.ndarray:
        """Translate the coordinates by the given xy values.

        :param homogeneous_coordinates: The coordinates to translate
        :type homogeneous_coordinates: :class:`numpy.ndarray`
        :returns: The translated coordinates
        :rtype: :class:`numpy.ndarray`
        """
        translation_matrix = np.array([[1, 0, self.x],
                                       [0, 1, self.y],
                                       [0, 0, 1]])

        translate_point = partial(_apply_transformation_matrix_on_point, translation_matrix)
        return np.apply_along_axis(translate_point, 2, homogeneous_coordinates)


class RotateTransformation:
    """Apply rotation transformation."""

    def __init__(self, angle: float, is_radian: bool=False):
        """Initialize the rotation transformation.

        :param angle: The angle by which to rotate the figure
        :type angle: float
        :param is_radian: Is the angle in radians
        :type is_radian: bool
        """
        self.angle = math.radians(angle) if not is_radian else angle

    def apply(self, homogeneous_coordinates: np.ndarray) -> np.ndarray:
        """Apply the rotation to the given coordinates.

        :param homogeneous_coordinates: The coordinates to rotate
        :type homogeneous_coordinates: :class:`numpy.ndarray`
        :returns: The rotated coordinates
        :rtype: :class:`numpy.ndarray`
        """
        return self._rotate(homogeneous_coordinates)

    def _rotate(self, homogeneous_coordinates: np.ndarray) -> np.ndarray:
        """Rotate the figure by the specified angle.

        :param homogeneous_coordinates: The coordinates to rotate
        :type homogeneous_coordinates: :class:`numpy.ndarray`
        :returns: The rotated coordinates
        :rtype: :class:`numpy.ndarray`
        """
        rotation_matrix = np.array([[np.cos(self.angle), -np.sin(self.angle), 0],
                                    [np.sin(self.angle), np.cos(self.angle), 0],
                                    [0, 0, 1]])
        x, y = compute_coordinates_center(
            convert_to_cartesian_coordinates(homogeneous_coordinates),
            float
        )

        translate_transformation = TranslateTransformation(-x, -y)
        translated_points = translate_transformation.apply(homogeneous_coordinates)

        rotate_point = partial(_apply_transformation_matrix_on_point, rotation_matrix)
        rotated_coordinates = np.apply_along_axis(rotate_point, 2, translated_points)

        translate_transformation.x, translate_transformation.y = x, y
        return translate_transformation.apply(rotated_coordinates)


def _apply_transformation_matrix_on_point(transformation_matrix: np.ndarray,
                                          point: np.ndarray) -> np.ndarray:
    """Apply a transformation matrix on a point vector.

    :param transformation_matrix: The transformation matrix to apply
    :type transformation_matrix: :class:`numpy.ndarray`
    :param point: The point on which to apply the transformation
    :type point: :class:`numpy.ndarray`
    :returns: The transformed point
    :rtype: :class:`numpy.ndarray`
    """
    return transformation_matrix @ point


def convert_to_homogeneous_coordinates(coordinates: np.ndarray) -> np.ndarray:
    """Convert the given coordinates to homogeneous coordinates.

    :param coordinates: The coordinates to convert
    :type coordinates: :class:`numpy.ndarray`
    :returns: The homogeneous coordinates
    :rtype: :class:`numpy.ndarray`
    """
    return np.append(coordinates,
                     np.ones((coordinates.shape[0], 1, 1)),
                     axis=2)


def convert_to_cartesian_coordinates(coordinates: np.ndarray) -> np.ndarray:
    """Convert the given coordinates to cartesian coordinates.

    :param coordinates: The coordinates to convert
    :type coordinates: :class:`numpy.ndarray`
    :returns: The cartesian coordinates
    :rtype: :class:`numpy.ndarray`
    """
    return np.delete(coordinates, 2, axis=2).astype(np.int32)
