import cv2

import os
import time
from typing import Any, List

import design.vision.constants as constants


class Camera:
    def __init__(self):
        self.camera_port = 0
        self.camera = cv2.VideoCapture()

    def set_camera_port(self, port=0):
        """
        :param port: port number of camera (default 0 if there's a single camera)
        """
        self.camera_port = port

    def open_camera(self):
        self.camera = cv2.VideoCapture(self.camera_port)

    def close_camera(self):
        self.camera.release()  # When everything done, release the capture

    def set_image_size(self, width=1280, height=720):
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    def set_frames_per_second(self, frames_per_second=1):
        self.camera.set(5, frames_per_second)

    def get_frames(self, number_of_frames=1, write=1, folder=''):

        if not folder:
            folder = 'data'
        # we create the directory
        if not os.path.isdir(folder):
            os.mkdir(folder)

        if self.camera.isOpened():
            for _ in range(number_of_frames):
                print("Capturing frame")
                return_value, frame = self.camera.read()
                if return_value == 0:
                    print("No image has been captured")
                else:
                    if write:
                        timestamp = time.time()
                        file = "./{}/capture{}.png".format(folder, timestamp)
                        cv2.imwrite(file, frame)

    def print_actual_settings(self):
        if self.camera.isOpened():
            print("hue is {}".format(self.camera.get(cv2.CAP_PROP_HUE)))
            print("saturation is {}".format(self.camera.get(cv2.CAP_PROP_SATURATION)))
            print("brightness is {}".format(self.camera.get(cv2.CAP_PROP_BRIGHTNESS)))
            print("exposure is {}".format(self.camera.get(cv2.CAP_PROP_EXPOSURE)))
            print("gain is {}".format(self.camera.get(cv2.CAP_PROP_GAIN)))

    def set_camera_settings(self, contrast, saturation, brightness, exposure, gain):
        self.camera.set(cv2.CAP_PROP_CONTRAST, contrast)
        self.camera.set(cv2.CAP_PROP_BRIGHTNESS, brightness)
        self.camera.set(cv2.CAP_PROP_SATURATION, saturation)
        self.camera.set(cv2.CAP_PROP_EXPOSURE, exposure)
        self.camera.set(cv2.CAP_PROP_AUTOFOCUS, 0)
        self.camera.set(cv2.CAP_PROP_GAIN, gain)


class CameraInMemory:
    """A camera that do not save the images in the file system but returns the
       pictures as objects instead.
    """

    def __init__(self, port: int, settings: CameraSettings):
        """Initialize the :class:`design.vision.camera.CameraInMemory`.

        :param port: The port of the camera on the machine
        :type port: int
        :param settings: The settings of the camera (i.e. contrast, brightness,
                         etc.)
        :type settings: :class:`design.vision.camera.CameraSettings`
        """
        self.camera = None
        self.port = port
        self.settings = settings

    def __enter__(self):
        """Enter the context manager and open the camera."""
        self.open()

    def open(self):
        """Open the camera with the given settings."""
        self.camera = cv2.VideoCapture(self.port)
        self.camera.set(cv2.CAP_PROP_AUTOFOCUS, False)
        self.update_camera_settings()

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

    def take_pictures(self, pictures_number: int) -> List[Any]:
        """Take the given number of pictures with the camera.

        :param pictures_number: The number of pictures to take
        :type pictures_number: int
        :returns: The pictures that were successfully taken
        """
        pictures = []
        if self.camera and self.camera.isOpened():
            for _ in range(pictures_number):
                picture_taken, picture = self.camera.read()
                if picture_taken:
                    pictures.append(picture)

        return pictures

    def set_camera_settings(self, settings: CameraSettings):
        """Set the camera's settings.

        :param settings: The camera's settings
        :type settings: :class:`design.vision.camera.CameraSettings`
        """
        self.settings = settings
        self.update_camera_settings()

    def update_camera_settings(self):
        """Update the camera's settings."""
        if self.camera:
            self.camera.set(cv2.CAP_PROP_BRIGHTNESS, self.settings.brightness)
            self.camera.set(cv2.CAP_PROP_CONTRAST, self.settings.contrast)
            self.camera.set(cv2.CAP_PROP_EXPOSURE, self.settings.exposure)
            self.camera.set(cv2.CAP_PROP_GAIN, self.settings.gain)
            self.camera.set(cv2.CAP_PROP_SATURATION, self.settings.saturation)
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.settings.width)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.settings.height)


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
        self.width = kwargs.get('width', 640)
        self.height = kwargs.get('height', 480)


def get_frames(camera, camera_number, number_of_frames=1):
    contrast, saturation, brightness, exposure, gain = constants.OPTIMIZED_CAMERA_VALUES[camera_number]
    camera.set_camera_port(1)
    camera.set_frames_per_second(1)
    camera.open_camera()
    camera.set_image_size()
    for i in range(5):
        print("Starting in {} seconds".format(5 - i))
        time.sleep(1)
    for _ in range(number_of_frames):
        camera.set_camera_settings(contrast, saturation, brightness, exposure, gain)
        time.sleep(5)
        camera.get_frames(1, folder='camera{}'.format(camera_number))
        print("Prepare to get frame..")
    camera.close_camera()
