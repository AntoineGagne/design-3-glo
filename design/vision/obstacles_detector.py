import cv2
import numpy as np
import math

import design.vision.constants as constants
from design.vision.world_utils import (calculate_angle,
                                       define_cardinal_point,
                                       eliminate_close_points,
                                       triangle_shortest_edge,
                                       calculate_centroid,
                                       eliminate_close_points_in_list)


class ObstaclesDetector:
    @property
    def actual_frame(self):
        return self._actual_frame

    @actual_frame.setter
    def actual_frame(self, frame):
        self._actual_frame = frame

    def __init__(self):
        self._actual_frame = None
        self.triangular_obstacles_coordinates = []
        self.obstacles_information = []

    def refresh_frame(self, image):
        self.actual_frame = image
        self.obstacles_information = []
        self.triangular_obstacles_coordinates = []

    def show_frame(self):
        cv2.imshow("this frame", self.actual_frame)
        cv2.waitKey(0)

    def __detect_obstacles_top_circles(self):
        """
        Detect top obstacles circles with Hough circles detection
        :return: image with top circles in aqua color
        :rtype: numpy.ndarray
        """
        gray = cv2.cvtColor(self.actual_frame, cv2.COLOR_BGR2GRAY)
        image_with_circles = self.actual_frame.copy()

        # circles detection
        circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1.2, 200,
                                   minRadius=constants.OBSTACLES_WHITE_CIRCLE_MIN_RADIUS)

        if circles is not None:
            circles = np.round(circles[0, :]).astype("int")
            for (x, y, radius) in circles:
                if constants.OBSTACLE_MIN_RADIUS < radius < constants.OBSTACLE_MAX_RADIUS:
                    # draw the circles to make mask afterwards
                    cv2.circle(image_with_circles, (x, y), radius, (255, 255, 0), -1)
        return image_with_circles

    def __show_obstacles_region_of_interest(self):
        """
        Only shows top of obstacles by applying mask on actual frame
        :return: masked image
        :rtype: numpy.ndarray
        """
        image_with_circles = self.__detect_obstacles_top_circles()
        aqua = np.array([255, 255, 0], dtype=np.uint8)
        masked_img = cv2.inRange(image_with_circles, aqua, aqua)
        masked_img = cv2.bitwise_and(self.actual_frame, self.actual_frame, mask=masked_img)
        return masked_img

    @staticmethod
    def __denoise_image(image):
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        filtered_image = cv2.bilateralFilter(gray_image, 10, 100, 100)

        kernel = np.ones((5, 5), np.uint8)
        morphed_image = cv2.morphologyEx(filtered_image, cv2.MORPH_OPEN, kernel)
        return morphed_image

    def __refine_image_contours(self):
        """
        Refines the contours of the obstacles' regions of interest with canny edge detection
        :return: binary image with well-defined contours
        :rtype: numpy.ndarray
        """
        masked_image = self.__show_obstacles_region_of_interest()
        denoised_image = self.__denoise_image(masked_image)
        canny_image = cv2.Canny(denoised_image, 100, 300, 3)
        return canny_image

    def __find_obstacles_contours(self):
        """
        Calculate obstacles' contours
        :return: contours
        :rtype: list
        """
        image = self.__refine_image_contours()
        _, contours, _ = cv2.findContours(image, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
        return contours

    def __detect_triangles(self):
        """
        Detect triangular obstacles
        The triangles coordinates and centroids will be stored in
        attribute triangles_obstacles
        """
        contours = self.__find_obstacles_contours()
        triangles_obstacles = []

        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            cx, cy = calculate_centroid(contour)

            high = constants.HIGHER_TRIANGLE_BOX_SIZE
            low = constants.LOWER_TRIANGLE_BOX_SIZE
            if high > w > low and high > h > low:
                perimeter = cv2.arcLength(contour, True)
                approximated_points = cv2.approxPolyDP(contour, 0.1 * perimeter, True)

                # we don't want too close points (imperfections from approxPolyDP)
                new_approximated_points = eliminate_close_points(approximated_points, 5)

                # identify triangles
                if len(new_approximated_points) == 3:
                    triangles_obstacles.append([[cx, cy], [new_approximated_points]])

        # eliminate duplicates (triangles on top of each other)
        self.triangular_obstacles_coordinates = eliminate_close_points(np.asarray(triangles_obstacles), 10)

    def __calculate_obstacle_orientation(self):
        """
        Calculate obstacle orientation for triangle obstacles
        Must be called after triangles are found
        """
        for t in range(len(self.triangular_obstacles_coordinates)):
            centroid = self.triangular_obstacles_coordinates[t][0]
            triangle_coordinates = self.triangular_obstacles_coordinates[t][1][0]
            shortest_edge_vertices = triangle_shortest_edge(triangle_coordinates)
            for coordinate in triangle_coordinates:
                if coordinate not in shortest_edge_vertices:
                    self.triangular_obstacles_coordinates[t] += tuple(
                        define_cardinal_point(calculate_angle(centroid, coordinate)))

    def __detect_circles(self):
        contours = self.__find_obstacles_contours()
        circles = []
        for contour in contours:
            (cx, cy), radius = cv2.minEnclosingCircle(contour)
            area_of_circle = 2 * math.pi * radius
            if 145 > area_of_circle > 120:
                circles.append((int(round(cx)), int(round(cy))))
                # only applies to 1200 x 1600 frames
        round_obstacles_information = eliminate_close_points_in_list(circles, 200)
        new_informations = []
        for information in round_obstacles_information:
            new_informations.append([information, "O"])
        self.obstacles_information.extend(new_informations)

        return self.obstacles_information

    def draw_obstacles(self):
        """
        Draws the found vertices on actual frame
        :return: image with drawn triangle vertices
        :rtype: numpy.ndarray
        """
        image = self.actual_frame.copy()
        for triangles in self.triangular_obstacles_coordinates:
            for triangle_coordinates in triangles[1]:
                for point in triangle_coordinates:
                    cv2.circle(image, point, 5, (222, 0, 233), -1)
        for obstacles in self.obstacles_information:
            if obstacles[1] == "O":
                cv2.circle(image, (obstacles[0][0], obstacles[0][1]), 20, (255, 255, 0), 3)

        smaller = cv2.resize(image, None, fx=0.5, fy=0.5)
        cv2.imshow("image", smaller)
        cv2.waitKey(0)
        return image

    def calculate_obstacles_information(self):
        """
        Get all pertinent obstacles information for actual frame
        :return: Coordinates and orientation of obstacles
        :rtype: list
        """
        self.__detect_triangles()
        self.__calculate_obstacle_orientation()
        self.__detect_circles()

        for triangle in self.triangular_obstacles_coordinates:
            self.obstacles_information.append([triangle[0], triangle[2]])
        return self.obstacles_information
