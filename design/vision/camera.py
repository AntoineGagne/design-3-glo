"""Contains the code related to cameras and taking pictures."""

import cv2

from typing import Any, Iterator
from subprocess import call


class Camera:
    """A camera that do not save the images in the file system but returns the
       pictures as objects instead.
    """

    def __init__(self,
                 port: int,
                 settings: 'CameraSettings',
                 manual_configuration: bool = False) -> None:
        """Initialize the :class:`design.vision.camera.CameraInMemory`.

        :param port: The port of the camera on the machine
        :type port: int
        :param settings: The settings of the camera (i.e. contrast, brightness,
                         etc.)
        :type settings: :class:`design.vision.camera.CameraSettings`
        """
        self.camera = None
        self.manual_configuration = manual_configuration
        self.port = port
        self.settings = settings

    def __enter__(self) -> 'Camera':
        """Enter the context manager and open the camera.

        :returns: The context manager
        :rtype: :class:`design.vision.camera.Camera`
        """
        self.open()
        return self

    def open(self):
        """Open the camera with the given settings."""
        self.camera = cv2.VideoCapture(self.port)
        self.set_camera_settings()

    def __exit__(self, exception_type, exception_value, exception_traceback):
        """Exit the context manager and close the camera.

        :param exception_type: The exception's type
        :param exception_value: The exception's value
        :param exception_traceback: The exception's traceback

        .. note:: Those exception parameters are all *None* if no exceptions
                  were raised. Also, since the exceptions are not handled, they
                  will propagate to the outer scope.
        """
        self.close()

    def close(self):
        """Close the camera."""
        self.camera.release()

    def take_pictures(self, pictures_number: int) -> Iterator[Any]:
        """Take the given number of pictures with the camera.

        :param pictures_number: The number of pictures to take
        :type pictures_number: int
        :returns: The pictures that were successfully taken
        """
        if self.camera and self.camera.isOpened():
            for _ in range(pictures_number):
                yield from self.take_picture()

    def stream_pictures(self) -> Iterator[Any]:
        """Take an infinite number of pictures as long as the camera is still
           open.

        :returns: A lazy stream of pictures
        """
        while self.camera and self.camera.isOpened():
            yield from self.take_picture()

    def take_picture(self) -> Iterator[Any]:
        """Take a single picture.

        :returns: A single picture
        """
        picture_taken, picture = self.camera.read()
        if picture_taken:
            yield picture

    def set_camera_settings(self):
        """Set the camera's settings."""
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.settings.width)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.settings.height)
        if self.manual_configuration:
            self.camera.set(cv2.CAP_PROP_SETTINGS, True)
        else:
            self._set_camera_settings()

    def _set_camera_settings(self):
        program_string = ('uvcdynctrl -s '
                          '\'Brightness\' {0} '
                          '\'Contrast\' {1} '
                          '\'Saturation\' {2} '
                          '\'Gain\' {3} '
                          '\'Exposure (Absolute)\' {4} '
                          '\'White Balance Temperature\' {5}').format(
            self.settings.brightness,
            self.settings.contrast,
            self.settings.saturation,
            self.settings.gain,
            self.settings.exposure,
            self.settings.white_balance_temperature)
        call(program_string, shell=True)


class CameraSettings:
    """A camera's settings."""

    def __init__(self, **kwargs):
        """Initialize a :class:`design.vision.camera.CameraSettings`.

        :param kwargs: See below

        :Keyword Arguments:
            * *brightness* (``int``) -- The brightness value of the camera
            * *contrast* (``int``) -- The contrast value of the camera
            * *exposure* (``int``) -- The exposure value of the camera
            * *gain* (``int``) -- The gain value of the camera
            * *saturation* (``int``) -- The saturation value of the camera
            * *width* (``int``) -- The width of the images taken
            * *height* (``int``) -- The height of the images taken
        """
        self.brightness = kwargs.get('brightness', 90)
        self.contrast = kwargs.get('contrast', 40)
        self.exposure = kwargs.get('exposure', 0)
        self.gain = kwargs.get('gain', 0)
        self.saturation = kwargs.get('saturation', 30)
        self.white_balance_temperature = kwargs.get('white_balance_temperature', 4000)
        self.width = kwargs.get('width', 640)
        self.height = kwargs.get('height', 480)
