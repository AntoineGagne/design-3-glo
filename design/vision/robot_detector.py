import math
import operator

import cv2

import design.vision.constants as constants
from design.vision.world_utils import (calculate_angle,
                                       triangle_shortest_edge,
                                       apply_segmentation,
                                       convert_to_degrees,
                                       calculate_norm)


class RobotDetector:
    @property
    def robot_position(self):
        return self._robot_position

    @robot_position.setter
    def robot_position(self, position):
        self._robot_position = position

    @property
    def actual_frame(self):
        return self._actual_frame

    @actual_frame.setter
    def actual_frame(self, frame):
        self._actual_frame = frame

    @property
    def robot_orientation(self):
        return self._robot_orientation

    @robot_orientation.setter
    def robot_orientation(self, orientation):
        self._robot_orientation = orientation

    @property
    def circles_coordinates(self):
        return self._circles_coordinates

    @circles_coordinates.setter
    def circles_coordinates(self, coordinates):
        self._circles_coordinates = coordinates

    def __init__(self):
        self._robot_position = (0, 0)
        self._robot_orientation = 0.0
        self._actual_frame = None
        self._circles_coordinates = []

    def refresh_frame(self, image):
        self.actual_frame = image
        self.circles_coordinates = []
        self.robot_position = (0, 0)
        self.robot_orientation = 0.0

    def __segment_frame(self):
        """
        only shows circular regions on top of the robot
        :return: BGR image showing only shapes on top of the robot
        :rtype: numpy.ndarray
        """
        segmented_frame = apply_segmentation(self.actual_frame, constants.MIN_MAGENTA, constants.MAX_MAGENTA)
        masked_image = cv2.bitwise_and(self.actual_frame, self.actual_frame, mask=segmented_frame)
        threshed_image = cv2.cvtColor(masked_image, cv2.COLOR_HSV2BGR)
        return threshed_image

    def __find_circles(self):
        """
        Find circles on top of the robot
        """
        frame = self.__segment_frame()
        gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        _, contours, _ = cv2.findContours(gray_image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            (cx, cy), radius = cv2.minEnclosingCircle(contour)
            if radius > constants.MIN_ROBOT_CIRCLE_RADIUS:
                self.circles_coordinates.append((cx, cy))
                cv2.circle(self.actual_frame, center=(int(cx), int(cy)), radius=2, color=(255, 0, 0), thickness=2)

    def __detect_robot_position(self):
        """
        The circles must make a triangle with
        the centroid being at the exact center of the robot
        so we can know its position according to its center
        """
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
        """
        Checks and finds the right set of three coordinates forming a triangle
        :return:
        """
        for i in range(len(self.circles_coordinates)):
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

    def __detect_robot_orientation(self):
        """
        Calculate orientation of the robot
        """
        if self.robot_position != (0, 0):
            shortest_edge_vertices = triangle_shortest_edge(self.circles_coordinates)
            for coordinate in self.circles_coordinates:
                if coordinate not in shortest_edge_vertices:
                    self.robot_orientation = round((180 - convert_to_degrees(calculate_angle(self.robot_position,
                                                                                             coordinate))) * -1, 2)

    def detect_robot(self):
        """
        Detect robot and get its position and orientation
        :return: robot position and orientation
        :rtype: list
        """
        self.__find_circles()
        self.__detect_robot_position()
        self.__detect_robot_orientation()
        print([self.robot_position, self.robot_orientation])
        self.display_robot()
        return [self.robot_position, self.robot_orientation]

    def display_robot(self):
        """
        Draw position and orientation of the robot on actual frame
        """
        draw_position(self.actual_frame, self.robot_position)
        draw_orientation(self.actual_frame, self.robot_orientation, self.robot_position)
        smaller = cv2.resize(self.actual_frame, None, fx=0.5, fy=0.5)
        cv2.imshow("image", smaller)
        cv2.waitKey(0)


def draw_position(image, point, color=(0, 0, 255)):
    cv2.circle(image, (int(point[0]), int(point[1])), 5, color, -1)


def draw_orientation(image, angle, centroid, color=(0, 0, 255), length=20, thickness=5):
    point2 = tuple(map(operator.add,
                       (length * math.cos(math.radians(angle)), length * math.sin(math.radians(angle))), centroid))
    cv2.line(image, (int(centroid[0]), int(centroid[1])), (int(point2[0]), int(point2[1])), color, thickness)
