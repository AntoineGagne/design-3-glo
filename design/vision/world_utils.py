import math
import cv2
import numpy as np

from design.vision.constants import (MAXIMUM_ANGLE_BETWEEN_SIMILAR_ANGLES,
                                     MAXIMUM_DISTANCE_BETWEEN_SIMILAR_COORDINATES)


def calculate_angle(point1, point2):
    return math.atan2(point1[1] - point2[1], point1[0] - point2[0])


def define_cardinal_point(angle):
    if angle < 0:
        orientation = "N"
    else:
        orientation = "S"
    return orientation


def calculate_norm(x1, y1, x2, y2):
    norm = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    return norm


def eliminate_duplicated_points(array, minimum_distance):
    keep = np.ones(array.shape, dtype=bool)
    for i, point_a in enumerate(array):
        x1, y1 = point_a[0]
        for k in range(i, len(array)):
            if i != k:
                x2, y2 = array[k][0]
                if calculate_norm(x1, y1, x2, y2) < minimum_distance:
                    keep[k] = False
    array = array[keep]
    new = list(zip(*[array[i::2] for i in range(2)]))
    return new


def eliminate_close_points_in_list(list_of_points, minimum_distance):
    array = np.asarray(list_of_points)
    keep = np.ones(array.shape, dtype=bool)
    for i, point_a in enumerate(array):
        x1, y1 = point_a
        for j, point_b in enumerate(array):
            if i != j:
                x2, y2 = point_b
                if calculate_norm(x1, y1, x2, y2) < minimum_distance:
                    keep[j] = False
    array = array[keep]
    new = list(zip(*[array[i::2] for i in range(2)]))
    new = [list(row) for row in new]
    return new


def get_best_information(list_of_information):
    already_associated_information = []
    associated_information = {}
    most_popular_information = 0
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
    for key, value in associated_information.items():
        if len(value) > len(associated_information[most_popular_information]):
            most_popular_information = key

    return list_of_information[most_popular_information]


def check_if_both_information_are_similar(information1, information2):
    if type(information1[0]) == list:
        return are_obstacles_information_similar(information1, information2)
    if type(information1[0]) == tuple:
        if type(information1[1]) == tuple:
            return are_drawing_zone_information_similar(information1, information2)
        if type(information1[1]) == float:
            return are_robot_information_similar(information1, information2)


def are_robot_information_similar(information1, information2):
    (x1, y1), orientation1 = information1
    (x2, y2), orientation2 = information2
    if abs(orientation1 - orientation2) > MAXIMUM_ANGLE_BETWEEN_SIMILAR_ANGLES:
        return False
    if calculate_norm(x1, y1, x2, y2) > MAXIMUM_DISTANCE_BETWEEN_SIMILAR_COORDINATES:
        return False
    return True


def are_drawing_zone_information_similar(information1, information2):
    similar_information = {}
    eliminated_information = []
    if len(information1) != len(information2):
        return False
    else:
        for i, point_a in enumerate(information1):
            x1, y1 = point_a
            for j, point_b in enumerate(information2):
                if j not in eliminated_information:
                    x2, y2 = point_b
                    if calculate_norm(x1, y1, x2, y2) < MAXIMUM_DISTANCE_BETWEEN_SIMILAR_COORDINATES:
                        similar_information[i] = j
                        eliminated_information.append(j)
                        break
        return len(similar_information) == len(information1)


def are_obstacles_information_similar(information1, information2):
    similar_informations = {}
    eliminated_information = []
    if not len(information1) == len(information2):
        return False
    else:
        for i, point_a in enumerate(information1):
            x1, y1 = point_a[0]
            orientation1 = point_a[1]
            for j, point_b in enumerate(information2):
                if j not in eliminated_information:
                    x2, y2 = point_b[0]
                    orientation2 = point_b[1]
                    if orientation1 != orientation2:
                        continue
                    if calculate_norm(x1, y1, x2, y2) < MAXIMUM_DISTANCE_BETWEEN_SIMILAR_COORDINATES:
                        similar_informations[i] = j
                        eliminated_information.append(j)
                        break
        return len(similar_informations) == len(information1)


def undistort_image(image, camera_matrix, distortion_coefficients):
    """
        Code edited from OpenCV samples documentation
    """
    height, width = image.shape[:2]
    undistorted_camera_matrix, region_of_interest = \
        cv2.getOptimalNewCameraMatrix(camera_matrix, distortion_coefficients, (width, height), 1, (width, height))
    undistorted_image = cv2.undistort(image, camera_matrix, distortion_coefficients, None, undistorted_camera_matrix)
    x, y, width, height = region_of_interest
    undistorted_image = undistorted_image[y:y + height, x:x + width]
    return undistorted_image, undistorted_camera_matrix


def triangle_shortest_edge(triangle_coordinates):
    shortest_edge = None
    minimal_length = math.inf
    for i, coordinates_a in enumerate(triangle_coordinates):
        x1, y1 = coordinates_a
        for k in range(i, len(triangle_coordinates)):
            if i != k:
                x2, y2 = triangle_coordinates[k]
                distance = calculate_norm(x1, y1, x2, y2)
                if distance < minimal_length:
                    minimal_length = distance
                    shortest_edge = [(x1, y1), (x2, y2)]
    return shortest_edge


def apply_segmentation(image, minimal_color_range, maximal_color_range):
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    segmented_image = cv2.inRange(hsv_image,
                                  np.array(minimal_color_range, np.uint8),
                                  np.array(maximal_color_range, np.uint8))
    return segmented_image


def calculate_centroid(contour):
    moment = cv2.moments(contour)
    cx, cy = 0, 0
    if moment['m00'] != 0:
        cx = int(moment['m10'] / moment['m00'])
        cy = int(moment['m01'] / moment['m00'])
    return cx, cy


def calculate_minimal_box_area(contour):
    rectangle = cv2.minAreaRect(contour)
    box = cv2.boxPoints(rectangle)
    box = np.int_(box)
    return cv2.contourArea(box)


def convert_to_degrees(angle_in_radians):
    return (math.degrees(angle_in_radians) + 360) % 360
