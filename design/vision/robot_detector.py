import cv2
import numpy

import design.vision.constants as constants
from design.vision.exceptions import RobotNotFound
from design.vision.world_utils import (calculate_angle,
                                       triangle_shortest_edge,
                                       apply_segmentation,
                                       convert_to_degrees,
                                       calculate_norm)


class RobotDetector:
    def __init__(self):
        self.robot_position = (0, 0)
        self.robot_orientation = 0.0
        self.circles_coordinates = []

    @staticmethod
    def segment_frame(frame: numpy.ndarray):
        segmented_frame = apply_segmentation(frame, constants.MIN_MAGENTA, constants.MAX_MAGENTA)
        masked_image = cv2.bitwise_and(frame, frame, mask=segmented_frame)
        threshed_image = cv2.cvtColor(masked_image, cv2.COLOR_HSV2BGR)
        eroded_image = cv2.erode(threshed_image, (5, 5), iterations=5)
        dilated_image = cv2.dilate(eroded_image, (5, 5), iterations=5)
        return dilated_image

    def find_circles(self, frame: numpy.ndarray):
        frame = self.segment_frame(frame)
        gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, contours, _ = cv2.findContours(gray_image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            (cx, cy), radius = cv2.minEnclosingCircle(contour)
            if radius > constants.MIN_ROBOT_CIRCLE_RADIUS:
                self.circles_coordinates.append((cx, cy))

    def detect_robot_position(self):
        if 3 < len(self.circles_coordinates):
            self.keep_valid_coordinates()
        if len(self.circles_coordinates) == 3:
            cx = 0
            cy = 0
            for point in self.circles_coordinates:
                cx += point[0]
                cy += point[1]
            self.robot_position = (round(cx / 3), round(cy / 3))

    def keep_valid_coordinates(self):
        for i, _ in enumerate(self.circles_coordinates):
            for j in range(i + 1, len(self.circles_coordinates)):
                if i != j:
                    for k in range(j + 1, len(self.circles_coordinates)):
                        if k != i and k != j:
                            first_side = calculate_norm(self.circles_coordinates[i][0], self.circles_coordinates[i][1],
                                                        self.circles_coordinates[j][0], self.circles_coordinates[j][1])
                            second_side = calculate_norm(self.circles_coordinates[i][0], self.circles_coordinates[i][1],
                                                         self.circles_coordinates[k][0], self.circles_coordinates[k][1])
                            third_side = calculate_norm(self.circles_coordinates[j][0], self.circles_coordinates[j][1],
                                                        self.circles_coordinates[k][0], self.circles_coordinates[k][1])

                            semi_perimeter = (first_side + second_side + third_side) / 2
                            area = (semi_perimeter * (semi_perimeter - first_side) * (semi_perimeter - second_side) * (
                                semi_perimeter - third_side)) ** 0.5
                            if constants.ROBOT_TRIANGLE_MINIMAL_AREA < area < constants.ROBOT_TRIANGLE_MAXIMAL_AREA:
                                self.circles_coordinates = [
                                    (self.circles_coordinates[i][0], self.circles_coordinates[i][1]),
                                    (self.circles_coordinates[j][0], self.circles_coordinates[j][1]),
                                    (self.circles_coordinates[k][0], self.circles_coordinates[k][1])]
                                return

    def detect_robot_orientation(self):
        if self.robot_position != (0, 0):
            shortest_edge_vertices = triangle_shortest_edge(self.circles_coordinates)
            for coordinate in self.circles_coordinates:
                if coordinate not in shortest_edge_vertices:
                    self.robot_orientation = round((180 - convert_to_degrees(calculate_angle(self.robot_position,
                                                                                             coordinate))) * -1, 2)

    def reset_information(self):
        self.circles_coordinates = []
        self.robot_position = (0, 0)
        self.robot_orientation = 0.0

    def detect_robot(self, frame: numpy.ndarray):
        self.reset_information()
        self.find_circles(frame)
        self.detect_robot_position()
        self.detect_robot_orientation()
        robot_information = [self.robot_position, self.robot_orientation]

        if robot_information == [(0, 0), 0.0] or not robot_information:
            raise RobotNotFound

        return robot_information
