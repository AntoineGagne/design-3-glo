import math
import cv2
import numpy as np

from design.vision.constants import (MAXIMUM_ANGLE_BETWEEN_SIMILAR_ANGLES,
                                     MAXIMUM_DISTANCE_BETWEEN_SIMILAR_COORDINATES)


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


def eliminate_close_points_in_list(list_of_points, minimum_distance):
    """
    compares specific arguments with each other to detect if the
    coordinates are too close depending on minimal distance required
    :param list_of_points: list of lists that represents the points
    :param minimum_distance: minimum distance between coordinates
    :type list_of_points: list
    :return: a list which only contains non-duplicated values
    """
    array = np.asarray(list_of_points)
    keep = np.ones(array.shape, dtype=bool)
    for i in range(len(array)):
        x1 = array[i][0]
        y1 = array[i][1]
        for k in range(i, len(array)):
            if i != k:
                x2 = array[k][0]
                y2 = array[k][1]
                if calculate_norm(x1, y1, x2, y2) < minimum_distance:
                    keep[k] = False
    array = array[keep]
    new = list(zip(*[array[i::2] for i in range(2)]))
    new = [list(row) for row in new]
    return new


def get_best_information(list_of_information):
    """
    When given a list of multiple obstacles information, coming from multiple images,
    calculates the obstacles information that is most susceptible to be valid
    :param obstacles_information: multiples obstacles information lists to be compared against each other
    :type obstacles_information: list
    :param maximum_distance: maximum distance between corresponding obstacles coordinates
    :type maximum_distance: int
    :return: obstacles information that is most susceptible to be valid
    :rtype: list
    """
    already_associated_information = []
    associated_information = {}

    number_of_set_of_coordinates = len(list_of_information)
    for i in range(number_of_set_of_coordinates):
        if i not in already_associated_information:
            associated_information[i] = []
            for j in range(i + 1, number_of_set_of_coordinates):
                if j not in already_associated_information:
                    result = check_if_both_information_are_similar(list_of_information[i],
                                                                   list_of_information[j])
                    if result:
                        associated_information[i].append(j)
                        already_associated_information.append(j)

    most_popular_information = 0
    for key, value in associated_information.items():
        if len(value) > len(associated_information[most_popular_information]):
            most_popular_information = key

    return list_of_information[most_popular_information]


def check_if_both_information_are_similar(information1, information2):
    """
    Redirects to the right function according to information type of data
    :param information1: first information containing coordinates and possibly orientation
    :type information1: list
    :param information2: second information containing coordinates and possibly orientation
    :type information2: list
    :param maximum_distance: maximum distance between corresponding drawing zone coordinates
    :type maximum_distance: int
    :return: true if both given information have similar data, false otherwise
    :rtype: bool
    """
    if type(information1[0]) == list:
        return are_obstacles_information_similar(information1, information2)
    if type(information1[0]) == tuple:
        if type(information1[1]) == tuple:
            return are_drawing_zone_information_similar(information1, information2)
        if type(information1[1]) == float:
            return are_robot_information_similar(information1, information2)


def are_robot_information_similar(information1, information2):
    """
    Compares both given robot information, coming from two different images and
    returns true if they have similar coordinates and orientation
    :param information1: first robot information
    :type information1: list
    :param information2: second robot information
    :type information2: list
    :param maximum_distance: maximum distance between corresponding robot coordinates
    :type maximum_distance: int
    :return: true if robot information have similar data, false otherwise
    :rtype: bool
    """
    x1 = information1[0][0]
    y1 = information1[0][1]
    orientation1 = information1[1]
    x2 = information2[0][0]
    y2 = information2[0][1]
    orientation2 = information2[1]
    if abs(orientation1 - orientation2) > MAXIMUM_ANGLE_BETWEEN_SIMILAR_ANGLES:
        return False
    if calculate_norm(x1, y1, x2, y2) > MAXIMUM_DISTANCE_BETWEEN_SIMILAR_COORDINATES:
        return False
    return True


def are_drawing_zone_information_similar(information1, information2):
    """
    Compares both given drawing zone information, coming from two different images and
    returns true if they have similar coordinates
    :param information1: first drawing zone information
    :type information1: list
    :param information2: second drawing zone information
    :type information2: list
    :param maximum_distance: maximum distance between corresponding drawing zone coordinates
    :type maximum_distance: int
    :return: true if drawing zone coordinates have similar data, false otherwise
    :rtype: bool
    """
    answer = False
    similar_information = {}
    eliminated_information = []
    if len(information1) != len(information2):
        return False
    else:
        for i in range(len(information1)):
            x1 = information1[i][0]
            y1 = information1[i][1]
            for j in range(len(information2)):
                if j not in eliminated_information:
                    x2 = information2[j][0]
                    y2 = information2[j][1]
                    if calculate_norm(x1, y1, x2, y2) < MAXIMUM_DISTANCE_BETWEEN_SIMILAR_COORDINATES:
                        similar_information[i] = j
                        eliminated_information.append(j)
                        break
        if len(similar_information) == len(information1):
            answer = True
    return answer


def are_obstacles_information_similar(information1, information2):
    """
    Compares both given obstacles information, coming from two different images and
    returns true if they have the same number of obstacles, same orientation and similar coordinates
    :param information1: first obstacles information
    :type information1: list
    :param information2: second obstacles information
    :type information2: list
    :param maximum_distance: maximum distance between corresponding obstacles coordinates
    :type maximum_distance: int
    :return: true if obstacles have similar data, false otherwise
    :rtype: bool
    """
    answer = False
    similar_informations = {}
    eliminated_information = []
    if len(information1) != len(information2):
        return False
    else:
        for i in range(len(information1)):
            x1 = information1[i][0][0]
            y1 = information1[i][0][1]
            orientation1 = information1[i][1]
            for j in range(len(information2)):
                if j not in eliminated_information:
                    x2 = information2[j][0][0]
                    y2 = information2[j][0][1]
                    orientation2 = information2[j][1]
                    if orientation1 != orientation2:
                        continue
                    if calculate_norm(x1, y1, x2, y2) < MAXIMUM_DISTANCE_BETWEEN_SIMILAR_COORDINATES:
                        similar_informations[i] = j
                        eliminated_information.append(j)
                        break
        if len(similar_informations) == len(information1):
            answer = True
    return answer


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
