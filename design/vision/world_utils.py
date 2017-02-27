import math
import cv2
import numpy as np


def calculate_angle(point1, point2):
    """
    Calculate the angle between two points
    :param point1: first point
    :param point2: second point
    :type point1: tuple or list
    :type point2: tuple or list
    :return: angle between -pi and pi
    :rtype: float
    """
    return math.atan2(point1[1] - point2[1], point1[0] - point2[0])


def define_cardinal_point(angle):
    """
    Define the cardinal point between North and South according to given angle
    :param angle: angle to calculate (counter-clockwise)
    :return: N or S for North or South respectively
    :rtype: string
    """
    if angle < 0:
        orientation = "N"
    else:
        orientation = "S"
    return orientation


def calculate_norm(x1, y1, x2, y2):
    """
    Calculate the distance between two points
    :param x1: x value of the first point
    :param y1: y value of the first point
    :param x2: x value of the second point
    :param y2: y value of the second point
    :return: norm between the two points
    :rtype: float
    """
    norm = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    return norm


def eliminate_close_points(array, minimum_distance):
    """
    compares specific arguments with each other to detect if the
    coordinates are too close depending on minimal distance required
    :param array: array of points
    :param minimum_distance: minimum distance between coordinates
    :type array: numpy.ndarray
    :return: a list which only contains non-duplicated values
    """
    keep = np.ones(array.shape, dtype=bool)
    for i in range(len(array)):
        x1 = array[i][0][0]
        y1 = array[i][0][1]
        for k in range(i, len(array)):
            if i != k:
                x2 = array[k][0][0]
                y2 = array[k][0][1]
                if calculate_norm(x1, y1, x2, y2) < minimum_distance:
                    keep[k] = False
    array = array[keep]
    new = list(zip(*[array[i::2] for i in range(2)]))
    return new


def undistort_image(image, camera_matrix, distortion_coefficients):
    """
        Code edited from OpenCV samples documentation
    """
    height, width = image.shape[:2]

    undistorted_camera_matrix, region_of_interest = \
        cv2.getOptimalNewCameraMatrix(camera_matrix, distortion_coefficients, (width, height), 1, (width, height))

    # undistort the image
    undistorted_image = cv2.undistort(image, camera_matrix, distortion_coefficients, None, undistorted_camera_matrix)

    # crop and save the image
    x, y, width, height = region_of_interest
    undistorted_image = undistorted_image[y:y + height, x:x + width]
    return undistorted_image, undistorted_camera_matrix


def triangle_shortest_edge(triangle_coordinates):
    """
    Calculates the triangle's shortest edge
    :param triangle_coordinates: coordinates of triangle
    :return: shortest edge vertices of given triangle
    :rtype: list
    """
    shortest_edge = None
    minimal_length = math.inf
    for i in range(len(triangle_coordinates)):
        x1 = triangle_coordinates[i][0]
        y1 = triangle_coordinates[i][1]
        for k in range(i, len(triangle_coordinates)):
            if i != k:
                x2 = triangle_coordinates[k][0]
                y2 = triangle_coordinates[k][1]
                distance = calculate_norm(x1, y1, x2, y2)
                if distance < minimal_length:
                    minimal_length = distance
                    shortest_edge = [(x1, y1), (x2, y2)]
    return shortest_edge


def apply_segmentation(image, minimal_color_range, maximal_color_range):
    """
    :param image: image containing a green zone to segment
    :param minimal_color_range: minimum color values in range
    :param maximal_color_range: maximum color values in range
    :type image: numpy.ndarray
    :type minimal_color_range: list
    :type maximal_color_range: list
    :return: segmented image
    :rtype: numpy.ndarray
    """
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    segmented_image = cv2.inRange(hsv_image,
                                  np.array(minimal_color_range, np.uint8),
                                  np.array(maximal_color_range, np.uint8))
    return segmented_image


def calculate_centroid(contour):
    """
    Calculates the centroid of the given contour
    :param contour: contour
    :return: centroid
    :rtype: tuple
    """
    moment = cv2.moments(contour)
    cx = 0
    cy = 0
    if moment['m00'] != 0:
        cx = int(moment['m10'] / moment['m00'])  # centroid x
        cy = int(moment['m01'] / moment['m00'])  # centroid y
    return cx, cy


def calculate_minimal_box_area(contour):
    """
    Calculate the area of the contour's minimal enclosing box
    :param contour: contour of the area
    :type contour: list
    :return: area of the contour
    :rtype: float
    """
    rectangle = cv2.minAreaRect(contour)
    box = cv2.boxPoints(rectangle)
    box = np.int_(box)
    return cv2.contourArea(box)


def convert_to_degrees(angle_in_radians):
    """
    Convert given radians angle to degrees
    :param angle_in_radians: angle in counter-clockwise radians with range from -pi to pi
    :type angle_in_radians: float
    :return: clockwise angle in degrees
    :rtype: float
    """
    return (math.degrees(angle_in_radians) + 360) % 360
