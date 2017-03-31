import numpy as np
import json
import cv2
import math
from design.vision.constants import TOP_GAP_FROM_DRAWING_ZONE, LEFT_GAP_FROM_DRAWING_ZONE
from design.vision.world_utils import convert_to_degrees, calculate_angle
from design.vision.constants import TABLE_HEIGHT, TABLE_WIDTH

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

        self.translation_x = 0
        self.translation_y = 0

    def extract_calibration_information_from_json(self, table_number):
        file_path = "{}{}.json".format(DEFAULT_CALIBRATION_JSON_FILE_PATH, table_number)
        with open(file_path) as data_file:
            data = json.load(data_file)
            self.intrinsic_matrix = data["intrinsic_matrix"]
            self.rotation_vector = data["rotation_vector"]
            self.translation_vector = data["translation_vector"]

    def set_top_left_world_game_zone_coordinate(self, drawing_zone_top_left_world_coordinate, table_angle: float):
        """
        Will be used before pixel to world conversion to adjust according to table origin
        We make a rotation of table_angle around drawing_zone_top_left_world_coordinate
        """
        x = drawing_zone_top_left_world_coordinate[0]
        y = drawing_zone_top_left_world_coordinate[1]
        px = LEFT_GAP_FROM_DRAWING_ZONE
        py = TOP_GAP_FROM_DRAWING_ZONE
        angle = -math.radians(table_angle)
        new_x = ((x - px) * math.cos(angle) - (y - py) * math.sin(angle))
        new_y = ((x - px) * math.sin(angle) + (y - py) * math.cos(angle))

        return [new_x, new_y]

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
        return [new_coordinate[0] + self.translation_x, new_coordinate[1] + self.translation_y]

    def get_pixel_coordinates(self, x, y, z):
        x = x - self.translation_x
        y = y - self.translation_y
        pixel_coordinates = np.dot(self.complete_matrix, np.array([x, y, z, 1]))
        new_pixel = pixel_coordinates[:2] / pixel_coordinates[2]
        return (int(new_pixel[0]), int(new_pixel[1]))

    def set_origin(self, x_translation, y_translation):
        self.translation_x = -x_translation
        self.translation_y = -y_translation


def calculate_table_rotation(drawing_zone_final_information):
    rotation_angle_of_table = round(
        (180 - convert_to_degrees(calculate_angle(drawing_zone_final_information[0],
                                                  drawing_zone_final_information[1]))) * -1, 2)
    return rotation_angle_of_table


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


def extrapolate_table(top_left_corner_world, table_angle):
    angle = -math.radians(table_angle)
    x = top_left_corner_world[0]
    y = top_left_corner_world[1]

    top_right = (x + TABLE_WIDTH * math.cos(angle),
                 y + TABLE_WIDTH * math.sin(angle))

    bottom_left = (x + TABLE_HEIGHT * math.sin(angle),
                   y + TABLE_HEIGHT * math.cos(angle))

    px = -TABLE_WIDTH
    py = -TABLE_HEIGHT

    bottom_right = (((x - px) * math.cos(angle) - (y - py) * math.sin(angle)),
                    ((x - px) * math.sin(angle) + (y - py) * math.cos(angle)))

    return [(x, y), top_right, bottom_left, bottom_right]
