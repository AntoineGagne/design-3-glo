"""Contains code related to the detection of figure's vertices with a camera."""

from design.vision.camera import CameraInMemory
from design.vision.transformations import (Figure,
                                           RotateTransformation,
                                           ScaleTransformation)


class OnboardVision:
    """Encapsulate the detection of figure's vertices."""

    def __init__(self, vertices_finder, camera: CameraInMemory):
        """Initialize the :class:`design.vision.onboard_vision.OnboardVision`

        :param vertices_finder: The object containing the algorithm to find the
                                figure's vertices
        :param camera: The onboard camera
        """
        self.camera = camera
        self.vertices_finder = vertices_finder
        self.last_capture = None

    def capture(self):
        """Capture an image with the camera."""
        self.last_capture = self.camera.take_pictures(1)

    def get_captured_vertices(self, zoom: float, orientation: float) -> Figure:
        """Get the figure's vertices from the last captured image and apply the
           geometrical transformations on it.

        :param zoom: The zoom factor to apply on the figure
        :type zoom: float
        :param orientation: The orientation of the figure
        :type orientation: float
        :returns: The detected and transformed figure
        :rtype: :class:`design.vision.transformations.Figure`

        :raises :class:`design.vision.exceptions.VerticesNotFound`:
            If no vertices could be found in the image
        :raises :class:`design.vision.exceptions.PaintingFrameNotFound`:
            If the painting's frame could not be found in the image
        """
        figure = self.vertices_finder.find_vertices(self.last_capture)
        return figure.apply_transformations(
            ScaleTransformation(zoom),
            RotateTransformation(orientation)
        )
