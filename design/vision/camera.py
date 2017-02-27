import os
import cv2
import design.vision.constants as constants
import time


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
