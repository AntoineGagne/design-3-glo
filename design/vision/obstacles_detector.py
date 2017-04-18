import cv2
import numpy
import numpy as np
import math
import design.vision.constants as constants
from design.vision.exceptions import ObstaclesNotFound
from design.vision.world_utils import (calculate_angle,
                                       define_cardinal_point,
                                       eliminate_duplicated_points,
                                       triangle_shortest_edge,
                                       calculate_centroid,
                                       eliminate_close_points_in_list)


class ObstaclesDetector:
    def __init__(self):
        self.triangular_obstacles_coordinates = []
        self.obstacles_information = []

    @staticmethod
    def __detect_obstacles_top_circles(frame: numpy.ndarray):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        image_with_circles = frame.copy()
        circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1.2, 200,
                                   minRadius=constants.OBSTACLES_WHITE_CIRCLE_MIN_RADIUS)

        if circles is not None:
            circles = np.round(circles[0, :]).astype("int")
            for (x, y, radius) in circles:
                if constants.OBSTACLE_MIN_RADIUS < radius < constants.OBSTACLE_MAX_RADIUS:
                    # draw the circles to make mask afterwards
                    cv2.circle(image_with_circles, (x, y), radius, (255, 255, 0), -1)
        return image_with_circles

    def __show_obstacles_region_of_interest(self, frame: numpy.ndarray):
        image_with_circles = self.__detect_obstacles_top_circles(frame)
        aqua = np.array([255, 255, 0], dtype=np.uint8)
        masked_img = cv2.inRange(image_with_circles, aqua, aqua)
        masked_img = cv2.bitwise_and(frame, frame, mask=masked_img)
        return masked_img

    @staticmethod
    def __denoise_image(image):
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        filtered_image = cv2.bilateralFilter(gray_image, 10, 100, 100)

        kernel = np.ones((5, 5), np.uint8)
        morphed_image = cv2.morphologyEx(filtered_image, cv2.MORPH_OPEN, kernel)
        return morphed_image

    def __refine_image_contours(self, frame: numpy.ndarray):
        masked_image = self.__show_obstacles_region_of_interest(frame)
        denoised_image = self.__denoise_image(masked_image)
        canny_image = cv2.Canny(denoised_image, 100, 300, 3)
        return canny_image

    def __find_obstacles_contours(self, frame: numpy.ndarray):
        image = self.__refine_image_contours(frame)
        _, contours, _ = cv2.findContours(image, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
        return contours

    def __detect_triangles(self, frame: numpy.ndarray):
        contours = self.__find_obstacles_contours(frame)
        triangles_obstacles = []

        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            cx, cy = calculate_centroid(contour)

            high = constants.HIGHER_TRIANGLE_BOX_SIZE
            low = constants.LOWER_TRIANGLE_BOX_SIZE
            if high > w > low and high > h > low:
                perimeter = cv2.arcLength(contour, True)
                approximated_points = cv2.approxPolyDP(contour, 0.1 * perimeter, True)

                new_approximated_points = eliminate_duplicated_points(approximated_points, 5)

                if len(new_approximated_points) == 3:
                    triangles_obstacles.append([[cx, cy], [new_approximated_points]])

        self.triangular_obstacles_coordinates = eliminate_duplicated_points(np.asarray(triangles_obstacles), 10)

    def __determine_obstacle_orientation(self):
        for t in range(len(self.triangular_obstacles_coordinates)):
            centroid = self.triangular_obstacles_coordinates[t][0]
            triangle_coordinates = self.triangular_obstacles_coordinates[t][1][0]
            shortest_edge_vertices = triangle_shortest_edge(triangle_coordinates)
            for coordinate in triangle_coordinates:
                if coordinate not in shortest_edge_vertices:
                    self.triangular_obstacles_coordinates[t] += tuple(
                        define_cardinal_point(calculate_angle(centroid, coordinate)))

    def __detect_circles(self, frame: numpy.ndarray):
        contours = self.__find_obstacles_contours(frame)
        circles = []
        for contour in contours:
            (cx, cy), radius = cv2.minEnclosingCircle(contour)
            area_of_circle = 2 * math.pi * radius
            if 150 > area_of_circle > 120:
                circles.append((int(round(cx)), int(round(cy))))
        round_obstacles_information = eliminate_close_points_in_list(circles, 200)
        new_informations = []
        for information in round_obstacles_information:
            new_informations.append([information, "O"])
        self.obstacles_information.extend(new_informations)

        return self.obstacles_information

    def calculate_obstacles_information(self, frame: numpy.ndarray):
        self.obstacles_information = []
        self.triangular_obstacles_coordinates = []

        self.__detect_triangles(frame)
        self.__determine_obstacle_orientation()
        self.__detect_circles(frame)

        for triangle in self.triangular_obstacles_coordinates:
            self.obstacles_information.append([triangle[0], triangle[2]])

        if not self.obstacles_information:
            raise ObstaclesNotFound

        return self.obstacles_information
