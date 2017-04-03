"""Contains code related to the detection of figure's vertices with a camera."""

import numpy as np

from itertools import chain
from typing import List

from design.vision.camera import Camera
from design.vision.transformations import (RotateTransformation,
                                           ScaleTransformation,
                                           WorldCoordinateTransformation)


class OnboardVision:
    def __init__(self, vertices_finder, camera: Camera) -> None:
        self.camera = camera
        self.vertices_finder = vertices_finder
        self.last_capture = None
        self.pixel_coordinates = None

    def capture(self):
        with self.camera:
            for picture in self.camera.take_pictures(1):
                self.last_capture = picture

    def get_captured_vertices(self,
                              zoom: float,
                              orientation: float) -> List[List[float]]:
        figure = self.vertices_finder.find_vertices(self.last_capture)
        self.pixel_coordinates = list(chain.from_iterable(figure.coordinates))

        transformed_figure = figure.apply_transformations(
            WorldCoordinateTransformation(),
            ScaleTransformation(zoom),
            RotateTransformation(orientation),
            datatype=np.float64
        )
        # OpenCV returns a matrix that looks like this:
        # [[[a, b]],
        #  ...
        #  [[y, z]]]
        # So we unpack it to remove the extra list from the result
        return list(chain.from_iterable(transformed_figure.coordinates))
