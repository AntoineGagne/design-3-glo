import cv2
import numpy as np

import time
from datetime import datetime
from itertools import chain
from typing import Any, List, Optional

from design.vision.camera import Camera
from design.vision.exceptions import (PaintingFrameNotFound,
                                      VerticesNotFound)
from design.vision.transformations import (RotateTransformation,
                                           ScaleTransformation,
                                           WorldCoordinateTransformation)
from design.vision.utils import swap_point
from design.vision.vertices import (find_best_figure,
                                    have_same_area_size,
                                    have_same_perimeter_size,
                                    have_same_center_position)


class OnboardVision:
    def __init__(self, vertices_finder, camera: Camera) -> None:
        self.camera = camera
        self.vertices_finder = vertices_finder
        self.last_capture = None
        self.pixel_coordinates = None
        self._captures = None

    def capture(self):
        with self.camera:
            self._captures = []
            for picture in self.camera.take_pictures(5):
                self._captures.append(picture)
                time.sleep(0.1)

    def get_captured_vertices(self,
                              zoom: float,
                              orientation: float) -> List[List[float]]:
        figures = list(map(self._find_vertices, self._captures))
        figure, index = find_best_figure(
            figures,
            have_same_area_size,
            have_same_perimeter_size,
            have_same_center_position
        )
        self.last_capture = self._captures[index]
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
        return [swap_point(point) for point
                in chain.from_iterable(transformed_figure.coordinates)]

    def _find_vertices(self, image) -> Optional[Any]:
        figure = None
        try:
            figure = self.vertices_finder.find_vertices(image)
        except PaintingFrameNotFound:
            cv2.imwrite(
                'PaintingFrameNotFound_{0}.jpg'.format(datetime.now()),
                image
            )
        except VerticesNotFound:
            cv2.imwrite(
                'VerticesNotFound_{0}.jpg'.format(datetime.now()),
                image
            )
        return figure
