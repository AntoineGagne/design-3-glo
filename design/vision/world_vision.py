import cv2
import numpy

from design.vision.drawing_zone_detector import DrawingZoneDetector
from design.vision.robot_detector import RobotDetector
from design.vision.obstacles_detector import ObstaclesDetector
from design.vision.conversion import Converter, calculate_table_rotation, set_top_left_world_game_zone_coordinate
from design.vision.camera import Camera
from design.vision.constants import NUMBER_OF_CAPTURES_TO_COMPARE, OBSTACLES_HEIGHT, ROBOT_HEIGHT, TABLE_WIDTH, \
    TABLE_HEIGHT, CROP_MARGIN
from design.vision.world_utils import get_best_information
from design.vision.exceptions import GameMapNotFound, RobotNotFound, DrawingZoneNotFound, ObstaclesNotFound


class WorldVision:
    def __init__(self, table_number: int,
                 obstacles_detector: ObstaclesDetector,
                 drawing_zone_detector: DrawingZoneDetector,
                 robot_detector: RobotDetector,
                 camera: Camera):

        self.camera = camera
        self.obstacles_detector = obstacles_detector
        self.drawing_zone_detector = drawing_zone_detector
        self.robot_detector = robot_detector
        self.converter = Converter(table_number)
        self.actual_frame = None

        self.game_map_pixels = {"drawing_zone": [],
                                "obstacles": [],
                                "robot": [],
                                "table_corners": [],
                                "base_obstacles": [],
                                "base_robot": []}
        self.game_map_world = {"drawing_zone": [],
                               "obstacles": [],
                               "robot": [],
                               "table_corners": []}

        self.rotation_angle_of_table = 0.0
        self.top_left_table_coordinate = None

    def get_world_game_map(self):
        self.game_map_world["drawing_zone"] = []
        self.game_map_world["obstacles"] = []
        self.game_map_pixels["base_obstacles"] = []

        for position in self.game_map_pixels["drawing_zone"]:
            world_position = self.converter.get_world_coordinates_translated(0,
                                                                             position[0],
                                                                             position[1])

            self.game_map_world["drawing_zone"].append((world_position[0], world_position[1]))

        self.detect_game_items()

        for information in self.game_map_pixels["obstacles"]:
            world_information = self.converter.get_world_coordinates_translated(OBSTACLES_HEIGHT,
                                                                                information[0][0],
                                                                                information[0][1])
            self.game_map_world["obstacles"].append([(world_information[0], world_information[1]), information[1]])
            self.game_map_pixels["base_obstacles"].append(
                self.converter.get_pixel_coordinates_translated(world_information[0], world_information[1], 0))

        self.game_map_world["robot"] = [tuple(self.converter.get_world_coordinates_translated(ROBOT_HEIGHT,
                                                                                              self.game_map_pixels[
                                                                                                  "robot"][0][0],
                                                                                              self.game_map_pixels[
                                                                                                  "robot"][0][1])),
                                        self.game_map_pixels["robot"][1]]
        self.game_map_pixels["base_robot"] = self.converter.get_pixel_coordinates_translated(
            self.game_map_world["robot"][0][0],
            self.game_map_world["robot"][0][1], 0)

        return self.game_map_world

    def detect_game_items(self):
        obstacles_information = []
        robot_information = []
        try:
            for picture in self.camera.take_pictures(NUMBER_OF_CAPTURES_TO_COMPARE):
                self.apply_image_crop()
                try:
                    obstacles_information.append(self.obstacles_detector.calculate_obstacles_information(picture))
                    robot_information.append(self.robot_detector.detect_robot(picture))
                except (RobotNotFound, ObstaclesNotFound):
                    pass

            self.set_game_map(obstacles_information, robot_information)
        except:
            raise GameMapNotFound

    def detect_static_items(self):
        drawing_zone_information = []
        try:
            for picture in self.camera.take_pictures(NUMBER_OF_CAPTURES_TO_COMPARE):
                try:
                    drawing_zone_information.append(self.drawing_zone_detector.find_drawing_zone_vertices(picture))
                    self.actual_frame = cv2.cvtColor(picture, cv2.COLOR_BGR2RGB)
                except DrawingZoneNotFound:
                    pass

            self.game_map_pixels["drawing_zone"] = get_best_information(drawing_zone_information)
            self.rotation_angle_of_table = calculate_table_rotation(self.game_map_pixels["drawing_zone"])
            self.adjust_converter()
            self.get_table_coordinates()
        except:
            raise DrawingZoneNotFound

        return self.game_map_pixels["drawing_zone"]

    def set_game_map(self,
                     obstacles_information: list,
                     robot_information: list):

        self.game_map_pixels["obstacles"] = get_best_information(obstacles_information)
        self.game_map_pixels["robot"] = get_best_information(robot_information)
        self.game_map_pixels["robot"][1] -= self.rotation_angle_of_table

    def detect_robot_fast(self):
        for picture in self.camera.take_picture():
            self.actual_frame = cv2.cvtColor(picture, cv2.COLOR_BGR2RGB)
            self.apply_image_crop()

            self.game_map_pixels["robot"] = self.robot_detector.detect_robot(picture)

            self.game_map_world["robot"] = [tuple(self.converter.get_world_coordinates_translated(ROBOT_HEIGHT,
                                                                                                  self.game_map_pixels[
                                                                                                      "robot"][0][0],
                                                                                                  self.game_map_pixels[
                                                                                                      "robot"][0][1])),
                                            self.game_map_pixels["robot"][1] - self.rotation_angle_of_table]
            self.game_map_pixels["base_robot"] = self.converter.get_pixel_coordinates_translated(
                self.game_map_world["robot"][0][0],
                self.game_map_world["robot"][0][1],
                0)

        return self.game_map_world["robot"]

    def get_table_coordinates(self):
        self.game_map_world["table_corners"] = [(0, 0),
                                                (TABLE_WIDTH, 0),
                                                (TABLE_WIDTH, TABLE_HEIGHT),
                                                (0, TABLE_HEIGHT)]

        for point in self.game_map_world["table_corners"]:
            table_pix = self.converter.get_pixel_coordinates_translated(int(point[0]), int(point[1]), 0)
            self.game_map_pixels["table_corners"].append(table_pix)

    def adjust_converter(self):
        temporary_world_drawing_zone = self.converter.get_world_coordinates(0,
                                                                            self.game_map_pixels["drawing_zone"][0][0],
                                                                            self.game_map_pixels["drawing_zone"][0][1])
        self.top_left_table_coordinate = set_top_left_world_game_zone_coordinate(
            temporary_world_drawing_zone, self.rotation_angle_of_table)
        self.converter.set_origin(self.top_left_table_coordinate[0], self.top_left_table_coordinate[1])

    def apply_image_crop(self):
        top_limit = self.game_map_pixels["table_corners"][0][1] - CROP_MARGIN
        bottom_limit = self.game_map_pixels["table_corners"][2][1] + CROP_MARGIN
        left_limit = self.game_map_pixels["table_corners"][0][0] - CROP_MARGIN
        mask = numpy.zeros(self.actual_frame.shape, numpy.uint8)
        mask[top_limit:bottom_limit, left_limit:1600] = self.actual_frame[top_limit:bottom_limit, left_limit:1600]
        self.actual_frame = mask
