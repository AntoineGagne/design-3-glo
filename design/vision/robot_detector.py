import math
import operator

import cv2

import design.vision.constants as constants
from design.vision.world_utils import calculate_angle, triangle_shortest_edge, apply_segmentation, convert_to_degrees


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

    def refresh_frame(self, path):
        self.actual_frame = cv2.imread(path)
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

    def __detect_robot_position(self):
        """
        The circles must make a triangle with
        the centroid being at the exact center of the robot
        so we can know its position according to its center
        """
        if len(self.circles_coordinates) == 3:
            cx = 0
            cy = 0
            for point in self.circles_coordinates:
                cx += point[0]
                cy += point[1]
            self.robot_position = (cx / 3, cy / 3)

    def __detect_robot_orientation(self):
        """
        Calculate orientation of the robot
        """
        centroid = self.robot_position
        triangle_coordinates = self.circles_coordinates
        if centroid != (0, 0):
            shortest_edge_vertices = triangle_shortest_edge(triangle_coordinates)

            for coordinate in triangle_coordinates:
                if coordinate not in shortest_edge_vertices:
                    self.robot_orientation = convert_to_degrees(calculate_angle(centroid, coordinate))

    def detect_robot(self):
        """
        Detect robot and get its position and orientation
        :return: robot position and orientation
        :rtype: list
        """
        self.__find_circles()
        self.__detect_robot_position()
        self.__detect_robot_orientation()
        return [self.robot_position, self.robot_orientation]

    def display_robot(self):
        """
        Draw position and orientation of the robot on actual frame
        """
        draw_position(self.actual_frame, self.robot_position)
        draw_orientation(self.actual_frame, self.robot_orientation, self.robot_position)
        cv2.imshow("robot", self.actual_frame)
        cv2.waitKey()


def draw_position(image, point, color=(0, 0, 255)):
    cv2.circle(image, (int(point[0]), int(point[1])), 5, color, -1)


def draw_orientation(image, angle, centroid, color=(0, 0, 255), length=20, thickness=5):
    point2 = tuple(map(operator.add,
                       (length * math.cos(math.radians(angle)), length * math.sin(math.radians(angle))), centroid))
    cv2.line(image, (int(centroid[0]), int(centroid[1])), (int(point2[0]), int(point2[1])), color, thickness)
