import numpy as np
import json
import cv2
import math
from design.vision.constants import TOP_GAP_FROM_DRAWING_ZONE, LEFT_GAP_FROM_DRAWING_ZONE

DEFAULT_CALIBRATION_JSON_FILE_PATH = "config/calibration_information_"


class Converter:
    def __init__(self, table_number):
        self.intrinsic_matrix = None
        self.rotation_vector = None
        self.translation_vector = None

        self.extract_calibration_information_from_json(table_number)

        self.extrinsic_matrix = calculate_extrinsic_matrix(self.rotation_vector,
                                                           self.translation_vector)
        self.complete_matrix = calculate_complete_camera_matrix(self.extrinsic_matrix,
                                                                self.intrinsic_matrix)
        self.origin = [0.0, 0.0]

    def extract_calibration_information_from_json(self, table_number):
        file_path = "{}{}.json".format(DEFAULT_CALIBRATION_JSON_FILE_PATH, table_number)
        with open(file_path) as data_file:
            data = json.load(data_file)
            self.intrinsic_matrix = data["intrinsic_matrix"]
            self.rotation_vector = data["rotation_vector"]
            self.translation_vector = data["translation_vector"]

    def set_origin(self, drawing_zone_top_left_world_coordinate, table_angle: float):
        """
        Will be used before pixel to world conversion to adjust according to table origin
        We make a rotation of table_angle around drawing_zone_top_left_world_coordinate
        :param drawing_zone_pixel_coordinates:
        :return:
        """
        new_x = (LEFT_GAP_FROM_DRAWING_ZONE * math.cos(table_angle) -
                 TOP_GAP_FROM_DRAWING_ZONE * math.sin(table_angle)) + drawing_zone_top_left_world_coordinate[0]
        new_y = (LEFT_GAP_FROM_DRAWING_ZONE * math.sin(table_angle) +
                 TOP_GAP_FROM_DRAWING_ZONE * math.cos(table_angle)) + drawing_zone_top_left_world_coordinate[1]

        self.origin = [new_x, new_y]

    def get_world_coordinates(self, height, u, v):
        a1 = [[] for i in range(0, 4)]
        a2 = [[] for i in range(0, 4)]
        a3 = [0, 0, 1, height]

        for i in range(0, 4):
            a1[i] = self.complete_matrix[0][i] - (u * self.complete_matrix[2][i])
            a2[i] = self.complete_matrix[1][i] - (v * self.complete_matrix[2][i])

        new_coordinate = -1 * (
            a1[3] * np.cross(np.array(a2)[0:3],
                             np.array(a3)[0:3]) +
            a2[3] * np.cross(np.array(a3)[0:3],
                             np.array(a1)[0:3]) +
            a3[3] * np.cross(np.array(a1)[0:3],
                             np.array(a2)[0:3])) / np.dot(np.array(a1[0:3]),
                                                          np.cross(np.array(a2[0:3]),
                                                                   np.array(a3[0:3])))
        new_coordinate = [new_coordinate[1] - self.origin[0], new_coordinate[0] - self.origin[1], new_coordinate[2]]
        return new_coordinate

    def get_pixel_coordinates(self, x, y, z):
        pixel_coordinates = np.dot(self.complete_matrix, np.array([x, y, z, 1]))
        return pixel_coordinates[:2] / pixel_coordinates[2]


def calculate_extrinsic_matrix(rotation_vector, translation_vector):
    """Get extrinsic matrix when we already have rotation and translation
       vectors.

    :param rotation_vector: rotation vector
    :type rotation_vector: :class:list
    :param translation_vector: translation vector
    :type translation_vector: :class:numpy.ndarray
    :return: Extrinsic 3x4 matrix
    :rtype: :class:numpy.ndarray
    """
    matrix = np.zeros(shape=(3, 3))
    cv2.Rodrigues(np.asarray(rotation_vector), matrix)
    return np.column_stack((matrix, translation_vector))


def calculate_complete_camera_matrix(extrinsic_matrix, intrinsic_matrix):
    return np.dot(intrinsic_matrix, extrinsic_matrix)
