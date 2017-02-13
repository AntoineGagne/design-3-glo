"""
    This is the main base station class
"""
import ui.main_ui
import time


class BaseStation:
    def __init__(self):
        self.__image_coordinates = []
        #   values_from_calibration = []
        self.__frame_coords = []

    # def set_frame_coordinates(self, set_of_points):
    #     # receives data from robot and stores it into attribute..

    def get_frame_coordinates(self):
        return self.__frame_coords

    def get_world_coordinates(self):
        return self.__image_coordinates

    # def convert_pixel_to_real_coords(self, pixel_coords):
    # def convert_real_to_pixel_coords(self, real_coords):
    # def calibrate_camera(self):