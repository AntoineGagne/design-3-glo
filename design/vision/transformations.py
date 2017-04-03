import math
from functools import partial, reduce

import cv2
import numpy as np

from .contours import compute_coordinates_center
from .constants import (PAINTING_DIMENSION_RATIO,
                        REAL_DRAWING_AREA_DIMENSION,
                        WARPED_IMAGE_DIMENSIONS,
                        WARPED_IMAGE_CORNERS)
from .utils import order_points


class PerspectiveWarper:
    def __init__(self,
                 destination_points=WARPED_IMAGE_CORNERS,
                 image_dimensions=WARPED_IMAGE_DIMENSIONS):
        self.destination_points = destination_points
        self.image_dimensions = image_dimensions

    def change_image_perspective(self, image, source_points):
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
    def __init__(self, coordinates: np.ndarray):
        self._homogeneous_coordinates = convert_to_homogeneous_coordinates(coordinates)
        self._coordinates = coordinates

    @property
    def coordinates(self) -> np.ndarray:
        return self._coordinates

    @coordinates.setter
    def coordinates(self, coordinates: np.ndarray):
        self._coordinates = coordinates
        self._homogeneous_coordinates = convert_to_homogeneous_coordinates(
            coordinates
        )

    def apply_transformations(self, *transformations, **kwargs) -> 'Figure':
        datatype = kwargs.get('datatype', np.int32)
        return Figure(
            convert_to_cartesian_coordinates(
                reduce(
                    lambda coordinates, transformation: transformation.apply(coordinates),
                    transformations,
                    self._homogeneous_coordinates
                ),
                datatype
            )
        )


class ScaleTransformation:
    def __init__(self, x: float, y: float=None):
        self.x = x
        self.y = y if y else x

    def apply(self, homogeneous_coordinates: np.ndarray) -> np.ndarray:
        return self._scale(homogeneous_coordinates)

    def _scale(self, homogeneous_coordinates: np.ndarray) -> np.ndarray:
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
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def apply(self, homogeneous_coordinates: np.ndarray) -> np.ndarray:
        return self._translate(homogeneous_coordinates)

    def _translate(self, homogeneous_coordinates: np.ndarray) -> np.ndarray:
        translation_matrix = np.array([[1, 0, self.x],
                                       [0, 1, self.y],
                                       [0, 0, 1]])

        translate_point = partial(_apply_transformation_matrix_on_point, translation_matrix)
        return np.apply_along_axis(translate_point, 2, homogeneous_coordinates)


class RotateTransformation:
    def __init__(self, angle: float, is_radian: bool=False):
        self.angle = math.radians(angle) if not is_radian else angle

    def apply(self, homogeneous_coordinates: np.ndarray) -> np.ndarray:
        return self._rotate(homogeneous_coordinates)

    def _rotate(self, homogeneous_coordinates: np.ndarray) -> np.ndarray:
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


class WorldCoordinateTransformation:
    def __init__(self,
                 factor: float=PAINTING_DIMENSION_RATIO,
                 drawing_border: float=REAL_DRAWING_AREA_DIMENSION) -> None:
        self.factor = factor
        self.drawing_border = drawing_border

    def apply(self, homogeneous_coordinates: np.ndarray) -> np.ndarray:
        return self._convert(homogeneous_coordinates)

    def _convert(self, homogeneous_coordinates: np.ndarray) -> np.ndarray:
        cartesian_coordinates = convert_to_cartesian_coordinates(
            homogeneous_coordinates
        )
        centroid_x, centroid_y = compute_coordinates_center(
            cartesian_coordinates
        )
        homogeneous_real_coordinates = self._convert_to_real_coordinates(
            cartesian_coordinates
        )
        translate_transformation = TranslateTransformation(
            self.drawing_border / 2 - centroid_x * self.factor,
            self.drawing_border / 2 - centroid_y * self.factor
        )
        return translate_transformation.apply(homogeneous_real_coordinates)

    def _convert_to_real_coordinates(self,
                                     cartesian_coordinates: np.ndarray) -> np.ndarray:
        real_coordinates = np.apply_along_axis(
            lambda x: x * self.factor,
            2,
            cartesian_coordinates
        )
        return convert_to_homogeneous_coordinates(real_coordinates)


def _apply_transformation_matrix_on_point(transformation_matrix: np.ndarray,
                                          point: np.ndarray) -> np.ndarray:
    return transformation_matrix @ point


def convert_to_homogeneous_coordinates(coordinates: np.ndarray) -> np.ndarray:
    return np.append(coordinates,
                     np.ones((coordinates.shape[0], 1, 1)),
                     axis=2)


def convert_to_cartesian_coordinates(coordinates: np.ndarray,
                                     datatype=np.int32) -> np.ndarray:
    return np.delete(coordinates, 2, axis=2).astype(datatype)
