import cv2
import numpy as np
import math
import design.vision.constants as constants
from design.vision.world_utils import apply_segmentation, calculate_minimal_box_area


class DrawingZoneDetector:
    @property
    def actual_frame(self):
        return self._actual_frame

    @actual_frame.setter
    def actual_frame(self, frame):
        self._actual_frame = frame

    def __init__(self):
        self.drawing_zone_coordinates = []
        self._actual_frame = None

    def refresh_frame(self, path):
        self.actual_frame = cv2.imread(path)
        self.drawing_zone_coordinates = []

    @staticmethod
    def apply_morphological_transformations(image):
        """
        :param image: image to transform
        :type image: numpy.ndarray
        :return: transformed image
        :rtype: numpy.ndarray
        """
        kernel = np.ones((5, 5), np.uint8)
        transformed_image = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)
        transformed_image = cv2.dilate(transformed_image, kernel, iterations=4)
        transformed_image = cv2.erode(transformed_image, kernel, iterations=4)
        return transformed_image

    @staticmethod
    def smooth_image(image):
        """
        :param image: image to smooth
        :type image: numpy.ndarray
        :return: smoothed image
        :rtype: numpy.ndarray
        """
        return cv2.GaussianBlur(image, (5, 5), 0)

    def apply_image_transformations(self):
        """
        Apply series of transformations on actual frame for pretreatment
        :return: transformed image
        :rtype: numpy.ndarray
        """
        thresh_image = apply_segmentation(self.actual_frame, constants.MIN_GREEN, constants.MAX_GREEN)
        smooth_image = self.smooth_image(thresh_image)
        morph_image = self.apply_morphological_transformations(smooth_image)
        return morph_image

    def find_drawing_zone_contours(self):
        """
        Apply pretreatment and find the contours of the image
        :return: found contours
        :rtype: list
        """
        pretreated_image = self.apply_image_transformations()
        _, contours, _ = cv2.findContours(pretreated_image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        return contours

    def find_drawing_zone_vertices(self):
        """
        Finds drawing zone vertices to delimit area
        :return: list of four coordinates
        :rtype: list
        """
        contours = self.find_drawing_zone_contours()
        minimal_area = math.inf
        minimal_approximated_contour = None
        for contour in contours:
            box_area = calculate_minimal_box_area(contour)
            perimeter = cv2.arcLength(contour, True)
            # approximate the contour with 1% precision (reduce number of vertices)
            approximate_contour = cv2.approxPolyDP(contour, 0.01 * perimeter, True)
            # set only one contour as the drawing zone
            for _ in approximate_contour:
                if len(approximate_contour) == 4 and box_area > constants.DRAWING_ZONE_MIN_AREA:
                    if box_area < minimal_area:
                        minimal_area = box_area
                        minimal_approximated_contour = approximate_contour
        if minimal_approximated_contour is not None:
            for i in minimal_approximated_contour:
                self.drawing_zone_coordinates.append(tuple(i[0]))

        return self.drawing_zone_coordinates
