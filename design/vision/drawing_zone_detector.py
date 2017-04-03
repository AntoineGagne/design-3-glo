import cv2
import numpy
import math
import design.vision.constants as constants
from design.vision.exceptions import DrawingZoneNotFound
from design.vision.world_utils import apply_segmentation, calculate_minimal_box_area


class DrawingZoneDetector:
    def __init__(self):
        self.drawing_zone_coordinates = []

    @staticmethod
    def apply_morphological_transformations(image: numpy.ndarray):
        kernel = numpy.ones((5, 5), numpy.uint8)
        transformed_image = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)
        transformed_image = cv2.dilate(transformed_image, kernel, iterations=4)
        transformed_image = cv2.erode(transformed_image, kernel, iterations=4)

        return transformed_image

    def __apply_image_transformations(self, image: numpy.ndarray):
        thresh_image = apply_segmentation(image, constants.MIN_GREEN, constants.MAX_GREEN)
        smooth_image = cv2.GaussianBlur(thresh_image, (5, 5), 0)
        morph_image = self.apply_morphological_transformations(smooth_image)
        return morph_image

    def __find_drawing_zone_contours(self, image: numpy.ndarray):
        pretreated_image = self.__apply_image_transformations(image)
        _, contours, _ = cv2.findContours(pretreated_image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        return contours

    def find_drawing_zone_vertices(self, image: numpy.ndarray):
        self.drawing_zone_coordinates = []

        contours = self.__find_drawing_zone_contours(image)
        minimal_area = math.inf
        minimal_approximated_contour = None
        for contour in contours:
            box_area = calculate_minimal_box_area(contour)
            perimeter = cv2.arcLength(contour, True)
            approximate_contour = cv2.approxPolyDP(contour, 0.01 * perimeter, True)
            for _ in approximate_contour:
                if len(approximate_contour) == 4 and box_area > constants.DRAWING_ZONE_MIN_AREA:
                    if box_area < minimal_area:
                        minimal_area = box_area
                        minimal_approximated_contour = approximate_contour
        if minimal_approximated_contour is not None:
            for i in minimal_approximated_contour:
                self.drawing_zone_coordinates.append(tuple(i[0]))

        if not self.drawing_zone_coordinates:
            raise DrawingZoneNotFound

        self.__reorder_drawing_zone_vertices()

        return self.drawing_zone_coordinates

    def __reorder_drawing_zone_vertices(self):
        approximate_center = [0, 0]
        for vertex in self.drawing_zone_coordinates:
            approximate_center[0] += vertex[0]
            approximate_center[1] += vertex[1]
        approximate_center[0] /= 4
        approximate_center[1] /= 4

        ordered_drawing_zone_coordinates = [(), (), (), ()]

        for vertex in self.drawing_zone_coordinates:
            if vertex[0] < approximate_center[0] and vertex[1] < approximate_center[1]:
                ordered_drawing_zone_coordinates[0] = vertex
            if vertex[0] > approximate_center[0] and vertex[1] < approximate_center[1]:
                ordered_drawing_zone_coordinates[1] = vertex
            if vertex[0] > approximate_center[0] and vertex[1] > approximate_center[1]:
                ordered_drawing_zone_coordinates[2] = vertex
            else:
                ordered_drawing_zone_coordinates[3] = vertex

        self.drawing_zone_coordinates = ordered_drawing_zone_coordinates
