from design.vision.drawing_zone_detector import DrawingZoneDetector
from design.vision.robot_detector import RobotDetector
from design.vision.obstacles_detector import ObstaclesDetector
from design.vision.conversion import Converter
from design.vision.camera import Camera
from design.vision.constants import NUMBER_OF_CAPTURES_TO_COMPARE, OBSTACLES_HEIGHT, ROBOT_HEIGHT
from design.vision.world_utils import (get_best_information,
                                       calculate_angle,
                                       convert_to_degrees)
from design.vision.exceptions import GameMapNotFound, RobotNotFound


class WorldVision:
    def __init__(self, table_number: int,
                 obstacles_detector: ObstaclesDetector,
                 drawing_zone_detector: DrawingZoneDetector,
                 robot_detector: RobotDetector,
                 camera: Camera):

        self.camera = camera
        self.actual_frame = None

        # these informations are in world coordinates
        self.actual_robot_information = None
        self.game_map = {}

        # this is useful for drawing in the UI
        self.game_map_in_pixels = {}

        self.rotation_angle_of_table = 0.0

        self.obstacles_detector = obstacles_detector
        self.drawing_zone_detector = drawing_zone_detector
        self.robot_detector = robot_detector

        self.converter = Converter(2)

        self.camera.open()

    def detect_obstacles(self):
        """
        Takes multiple pictures and gets obstacles information from it
        :return:
        """
        obstacles_information = []
        for picture in self.camera.take_pictures(NUMBER_OF_CAPTURES_TO_COMPARE):
            self.obstacles_detector.refresh_frame(picture)
            new_information = self.obstacles_detector.calculate_obstacles_information()
            if new_information != []:
                obstacles_information.append(new_information)

        obstacles_information = filter_information(obstacles_information)
        obstacles_final_information = get_best_information(obstacles_information)

        self.game_map_in_pixels["obstacles"] = obstacles_final_information

        obstacles_world_information = []
        for information in obstacles_final_information:
            world_information = self.converter.get_world_coordinates(OBSTACLES_HEIGHT,
                                                                     information[0][0],
                                                                     information[0][1])
            obstacles_world_information.append([(world_information[0], world_information[1]), information[1]])

        return obstacles_world_information

    def detect_robot(self):
        """
        Algorithm to call when vision performance is more important (might be riskier to not having robot detected)
        :return: new robot information
        """
        for picture in self.camera.take_picture():
            self.actual_frame = picture
        self.robot_detector.refresh_frame(self.actual_frame)
        actual_robot_information = self.robot_detector.detect_robot()

        if actual_robot_information == [(0, 0), 0.0]:
            raise RobotNotFound

        self.game_map_in_pixels["robot"] = actual_robot_information
        # [(448, 570), 18.53]
        robot_world_information = self.converter.get_world_coordinates(ROBOT_HEIGHT,
                                                                       actual_robot_information[0][0],
                                                                       actual_robot_information[0][1])
        # adjust angle according to table angle
        robot_angle = actual_robot_information[1] - self.rotation_angle_of_table
        self.actual_robot_information = [robot_world_information, robot_angle]

        return self.actual_robot_information

    def detect_robot_at_the_beginning(self):
        """
        Takes multiple pictures and gets robot information from it
        :return:
        """
        robot_information = []
        for picture in self.camera.take_pictures(NUMBER_OF_CAPTURES_TO_COMPARE):
            self.actual_frame = picture
            self.robot_detector.refresh_frame(picture)
            new_information = self.robot_detector.detect_robot()
            if new_information != []:
                robot_information.append(new_information)

        robot_information = filter_information(robot_information)
        robot_final_information = get_best_information(robot_information)

        if robot_final_information == [(0, 0), 0.0]:
            raise RobotNotFound

        self.game_map_in_pixels["robot"] = robot_final_information

        # adjust angle according to table angle
        robot_angle = robot_final_information[1] - self.rotation_angle_of_table

        world_information = self.converter.get_world_coordinates(ROBOT_HEIGHT,
                                                                 robot_final_information[0][0],
                                                                 robot_final_information[0][1])
        robot_world_information = [(world_information[0], world_information[1]), robot_angle]

        return robot_world_information

    def detect_drawing_zone(self):
        """
        Takes multiple pictures and gets drawing zone information from it
        Will be called only once at the beginning of the game
        :return:
        """
        drawing_zone_information = []
        for picture in self.camera.take_pictures(NUMBER_OF_CAPTURES_TO_COMPARE):
            self.drawing_zone_detector.refresh_frame(picture)
            new_information = self.drawing_zone_detector.find_drawing_zone_vertices()
            if new_information != []:
                drawing_zone_information.append(new_information)

        drawing_zone_information = filter_information(drawing_zone_information)
        drawing_zone_final_information = get_best_information(drawing_zone_information)

        # once the drawing zone is found, we are able to calculate the table's rotation
        self.rotation_angle_of_table = calculate_table_rotation(drawing_zone_final_information)
        self.game_map_in_pixels["drawing_zone"] = drawing_zone_final_information
        drawing_zone_top_left_world_coordinate = \
            self.converter.get_world_coordinates(0,
                                                 drawing_zone_final_information[0][0],
                                                 drawing_zone_final_information[0][1])
        self.converter.set_origin(drawing_zone_top_left_world_coordinate, self.rotation_angle_of_table)

        drawing_zone_world_coordinates = []
        for position in drawing_zone_final_information:
            world_position = self.converter.get_world_coordinates(0,
                                                                  position[0],
                                                                  position[1])

            drawing_zone_world_coordinates.append((world_position[0], world_position[1]))

        return drawing_zone_world_coordinates

    def get_initial_game_map(self):
        """
        Used at the beginning of the game, to send by telemetry
        :return: game map in world coordinates, in cm
        :rtype: dict
        """
        try:
            self.game_map["drawing_zone"] = self.detect_drawing_zone()
            self.game_map["obstacles"] = self.detect_obstacles()
            self.game_map["robot"] = self.detect_robot_at_the_beginning()
            # self.game_map["table_corners"] =
        except:
            raise GameMapNotFound

        return self.game_map

    def get_new_cycle_game_map(self):
        """
        Used at the beginning of a new cycle
        :return: game map in world coordinates, in cm
        :rtype: dict
        """
        try:
            self.game_map["obstacles"] = self.detect_obstacles()
            self.game_map["robot"] = self.detect_robot_at_the_beginning()
        except:
            raise GameMapNotFound
        return self.game_map

    def get_game_map_in_pixels(self):
        """
        Contains all data from game map but in pixels for drawing purposes
        Note : excludes the game zone coordinates (to be implemented)
        :return: game map in pixel coordinates
        :rtype: dict
        """
        return self.game_map_in_pixels


def calculate_table_rotation(drawing_zone_final_information):
    rotation_angle_of_table = round(
        (180 - convert_to_degrees(calculate_angle(drawing_zone_final_information[0],
                                                  drawing_zone_final_information[1]))) * -1, 2)
    return rotation_angle_of_table


def filter_information(information):
    return list(filter(any, information))
