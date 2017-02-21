import cv2
import design.vision.constants as constants
import time
import datetime

# 0. CV_CAP_PROP_POS_MSEC Current position of the video file in milliseconds.
# 1. CV_CAP_PROP_POS_FRAMES 0-based index of the frame to be decoded/captured next.
# 2. CV_CAP_PROP_POS_AVI_RATIO Relative position of the video file
# 15.CV_CAP_PROP_EXPOSURE Exposure (only for cameras).
# 16.CV_CAP_PROP_CONVERT_RGB Boolean flags indicating whether images should be converted to RGB.


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

    def set_image_size(self, width, height):
        self.camera.set(cv2.CV_CAP_PROP_FRAME_WIDTH, width)
        self.camera.set(cv2.CV_CAP_PROP_FRAME_HEIGHT, height)

    def set_fps(self, fps=1):
        self.camera.set(5, fps)

    def get_frames(self, number_of_frames=1, write=1, folder='data'):
        if self.camera.isOpened():
            for i in range(number_of_frames):
                print("Capturing frame #{}".format(i))
                retval, frame = self.camera.read()
                if retval == 0:
                    print("No image has been captured")
                else:
                    if write:
                        ts = time.time()
                        file = "./{}/capture{}.png".format(folder, ts)
                        cv2.imwrite(file, frame)

    def get_default_settings(self, camera_number):
        """
        :param camera_number: 0 if this is the onboard camera, 1 to 6 if world cameras
        according to corresponding table numbers
        """
        if self.camera.isOpened():
            constants.DEFAULT_CAMERA_VALUES[camera_number] = []
            for i in range(22):
                constants.DEFAULT_CAMERA_VALUES[camera_number].append(self.camera.get(i))
                print(self.camera.get(i))

    def set_contrast(self, value):
        self.camera.set(cv2.CAP_PROP_CONTRAST, value)

    def set_saturation(self, value):
        self.camera.set(cv2.CAP_PROP_SATURATION, value)

    def set_brightness(self, value):
        self.camera.set(cv2.CAP_PROP_BRIGHTNESS, value)

    def set_hue(self, value):
        self.camera.set(cv2.CAP_PROP_HUE, value)

    def set_gain(self, value):
        self.camera.set(cv2.CAP_PROP_GAIN, value)

    def set_exposure(self, value):
        self.camera.set(cv2.CAP_PROP_EXPOSURE, value)

    def set_default_camera_settings(self, camera_number):
        """
        :param camera_number: 0 if this is the onboard camera, 1 to 6 if world cameras
        according to corresponding table numbers
        """
        for i in range(constants.DEFAULT_CAMERA_VALUES[camera_number].size):
            self.camera.set(constants.DEFAULT_CAMERA_VALUES[camera_number][i])

    def set_optimized_camera_settings(self, camera_number):
        """
        :param camera_number: 0 if this is the onboard camera, 1 to 6 if world cameras
        according to corresponding table numbers
        """
        for i in range(constants.OPTIMIZED_CAMERA_VALUES[camera_number].size):
            self.camera.set(constants.OPTIMIZED_CAMERA_VALUES[camera_number][i])

if __name__ == '__main__':
    cam = Camera()
    cam.set_camera_port(1)
    cam.open_camera()
    # cam.get_default_settings(3)
    # print(constants.DEFAULT_CAMERA_VALUES)
    # cam.set_fps(1)
    # import time
    # time.sleep(15)
    # for i in range(20, 100):
    cam.set_brightness(244)
    # cam.camera.set(cv2.CAP_PROP_BRIGHTNESS, 255)
    print(cam.camera.get(cv2.CAP_PROP_BRIGHTNESS))
    cam.get_frames()
