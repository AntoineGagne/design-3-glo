import cv2

from typing import Any, Iterator
from subprocess import call


class Camera:
    def __init__(self,
                 port: int,
                 settings: 'CameraSettings',
                 manual_configuration: bool = False) -> None:
        self.camera = None
        self.manual_configuration = manual_configuration
        self.port = port
        self.settings = settings

    def __enter__(self) -> 'Camera':
        self.open()
        return self

    def open(self):
        self.camera = cv2.VideoCapture(self.port)
        self.set_camera_settings()

    def __exit__(self, exception_type, exception_value, exception_traceback):
        self.close()

    def close(self):
        self.camera.release()

    def take_pictures(self, pictures_number: int) -> Iterator[Any]:
        if self.camera and self.camera.isOpened():
            for _ in range(pictures_number):
                yield from self.take_picture()

    def stream_pictures(self) -> Iterator[Any]:
        while self.camera and self.camera.isOpened():
            yield from self.take_picture()

    def take_picture(self):
        picture_taken, picture = self.camera.read()
        if picture_taken:
            yield picture

    def set_camera_settings(self):
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
    def __init__(self, **kwargs):
        self.brightness = kwargs.get('brightness', 90)
        self.contrast = kwargs.get('contrast', 40)
        self.exposure = kwargs.get('exposure', 0)
        self.gain = kwargs.get('gain', 0)
        self.saturation = kwargs.get('saturation', 30)
        self.white_balance_temperature = kwargs.get('white_balance_temperature', 4000)
        self.width = kwargs.get('width', 640)
        self.height = kwargs.get('height', 480)
