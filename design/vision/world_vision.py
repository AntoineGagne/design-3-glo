from design.vision.drawing_zone_detector import DrawingZoneDetector
from design.vision.robot_detector import RobotDetector
from design.vision.obstacles_detector import ObstaclesDetector
from design.vision.conversion import Converter, calculate_table_rotation, extrapolate_table, \
    set_top_left_world_game_zone_coordinate
from design.vision.camera import Camera
from design.vision.constants import NUMBER_OF_CAPTURES_TO_COMPARE, OBSTACLES_HEIGHT, ROBOT_HEIGHT
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

        self.actual_robot_information = None

        self.game_map = {}  # values are in pixels
        self.world_game_map = {}  # values are in cm

        self.rotation_angle_of_table = 0.0
        self.top_left_table_coordinate = None

    def get_world_game_map(self, first_time: bool = True):

        self.detect_game_items(first_time)
        self.__adjust_converter()

        if first_time:
            self.world_game_map["drawing_zone"] = []
            for position in self.game_map["drawing_zone"]:
                world_position = self.converter.get_world_coordinates_translated(0,
                                                                                 position[0],
                                                                                 position[1])

                self.world_game_map["drawing_zone"].append((world_position[0], world_position[1]))

        self.world_game_map["obstacles"] = []
        for information in self.game_map["obstacles"]:
            world_information = self.converter.get_world_coordinates_translated(OBSTACLES_HEIGHT,
                                                                                information[0][0],
                                                                                information[0][1])
            self.world_game_map["obstacles"].append([(world_information[0], world_information[1]), information[1]])

        self.world_game_map["robot"] = [self.converter.get_world_coordinates_translated(ROBOT_HEIGHT,
                                                                                        self.game_map["robot"][0][0],
                                                                                        self.game_map["robot"][0][1]),
                                        self.game_map["robot"][1]]

        return self.world_game_map

    def detect_game_items(self, first_time: bool = True):
        drawing_zone_information = []
        obstacles_information = []
        robot_information = []

        try:
            for picture in self.camera.take_pictures(NUMBER_OF_CAPTURES_TO_COMPARE):
                try:
                    if first_time:
                        drawing_zone_information.append(self.drawing_zone_detector.find_drawing_zone_vertices(picture))
                    obstacles_information.append(self.obstacles_detector.calculate_obstacles_information(picture))
                    robot_information.append(self.robot_detector.detect_robot(picture))
                except (DrawingZoneNotFound, RobotNotFound, ObstaclesNotFound):
                    pass

            self.__set_game_map(drawing_zone_information, obstacles_information, robot_information, first_time)

        except:
            raise GameMapNotFound

    def __set_game_map(self,
                       drawing_zone_information: list,
                       obstacles_information: list,
                       robot_information: list,
                       first_time: bool):
        if first_time:
            self.game_map["drawing_zone"] = get_best_information(drawing_zone_information)
            self.rotation_angle_of_table = calculate_table_rotation(self.game_map["drawing_zone"])
            self.__adjust_converter()
            self.__get_table_coordinates()

        self.game_map["obstacles"] = get_best_information(obstacles_information)
        self.game_map["robot"] = get_best_information(robot_information)
        self.game_map["robot"][1] = self.game_map["robot"][1] - self.rotation_angle_of_table

    def detect_robot_fast(self):
        for picture in self.camera.take_picture():
            self.actual_frame = picture
            self.game_map["robot"] = self.robot_detector.detect_robot(picture)

        self.game_map["robot"][0] = self.converter.get_world_coordinates_translated(ROBOT_HEIGHT,
                                                                                    self.game_map["robot"][0][0],
                                                                                    self.game_map["robot"][0][1])
        self.game_map["robot"][1] -= self.rotation_angle_of_table

        return self.game_map["robot"]

    def __get_table_coordinates(self):
        temporary_table_corners = extrapolate_table(self.top_left_table_coordinate, self.rotation_angle_of_table)

        self.world_game_map["table_corners"] = []
        self.game_map["table_corners"] = []

        for point in temporary_table_corners:
            table_pix = self.converter.get_pixel_coordinates(int(point[0]), int(point[1]), 0)
            self.game_map["table_corners"].append(table_pix)
            self.world_game_map["table_corners"].append(self.converter.get_world_coordinates_translated(0,
                                                                                                        table_pix[0],
                                                                                                        table_pix[1]))

    def __adjust_converter(self):
        temporary_world_drawing_zone = self.converter.get_world_coordinates(0,
                                                                            self.game_map["drawing_zone"][0][0],
                                                                            self.game_map["drawing_zone"][0][1])
        self.top_left_table_coordinate = set_top_left_world_game_zone_coordinate(
            temporary_world_drawing_zone, self.rotation_angle_of_table)
        self.converter.set_origin(self.top_left_table_coordinate[0], self.top_left_table_coordinate[1])

    def get_new_cycle_game_map(self, first_time: bool = True):
        self.get_world_game_map(first_time)
        return self.world_game_map
