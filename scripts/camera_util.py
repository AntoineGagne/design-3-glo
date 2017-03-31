import cv2

import os
import time
from typing import Any, Sequence


class Camera:
    def __init__(self, width, height):
        self.camera_port = 0
        self.width = width
        self.height = height

    def set_camera_port(self, port=0):
        """
        :param port: port number of camera (default 0 if there's a single camera)
        """
        self.camera_port = port

    def open_camera(self):
        self.camera = cv2.VideoCapture(self.camera_port)
        self.set_image_resolution()
        self.camera.set(cv2.CAP_PROP_SETTINGS, 1)

    def close_camera(self):
        self.camera.release()  # When everything done, release the capture

    def set_image_resolution(self):
        if self.camera:
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

    def camera_is_opened(self):
        return self.camera.isOpened()

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


def get_frames(camera, camera_number, number_of_frames=1):
    camera.set_camera_port(1)
    camera.open_camera()
    for i in range(5):
        print("Starting in {} seconds".format(5 - i))
        time.sleep(1)
    for _ in range(number_of_frames):
        time.sleep(5)
        camera.get_frames(1, folder='camera{}'.format(camera_number))
        print("Prepare to get frame..")
    camera.close_camera()


if __name__ == "__main__":
    cam = Camera(1600, 1200)
    cam.set_camera_port(1)
    cam.open_camera()
    while cam.camera_is_opened():
        time.sleep(1)
        cam.get_frames(1, folder='camera_data')
        time.sleep(1)

# if table 4 camera port is 0
