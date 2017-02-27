import math

import numpy

import design.vision.world_utils as utils


def test_that_given_points_when_calculate_angle_then_angle_is_calculated():
    point1 = [10, 8]
    point2 = [-3, 2]
    angle = utils.calculate_angle(point1, point2)
    assert 0.43240777557053783 == angle


def test_that_given_angle_in_radians_when_define_cardinal_point_then_cardinal_point_is_defined():
    angle = - math.pi / 4
    cardinal_point = utils.define_cardinal_point(angle)
    assert "N" == cardinal_point


def test_than_given_points_when_calculate_norm_then_norm_is_calculated():
    point1 = [17, 21]
    point2 = [-3, -283]
    norm = utils.calculate_norm(point1[0], point1[1], point2[0], point2[1])
    assert 304.6571843892738 == norm


def test_that_given_array_when_eliminate_close_points_then_close_points_are_eliminated():
    array = numpy.array([[[666, 153]], [[709, 176]], [[686, 219]], [[643, 195]]])
    minimal_distance = 50
    new_array = (utils.eliminate_close_points(array, minimal_distance))
    assert new_array == [(666, 153)]


def test_that_given_triangle_coordinates_when_calculate_triangle_shortest_edge_then_triangle_shortest_edge_is_given():
    triangle_coordinates = [(0, 0), (10, 0), (5, 20)]
    shortest_edge_coordinates = utils.triangle_shortest_edge(triangle_coordinates)
    assert shortest_edge_coordinates == [(0, 0), (10, 0)]


def test_that_given_contour_centroid_when_calculate_centroid_then_centroid_is_calculated():
    contour = numpy.array([[[0, 0]], [[0, 10]], [[10, 10]], [[10, 0]]])
    centroid = utils.calculate_centroid(contour)
    assert (5, 5) == centroid


def test_that_given_contour_when_calculate_box_area_then_area_is_calculated():
    contour = numpy.array([[[0, 0]], [[0, 10]], [[10, 10]], [[10, 0]]])
    area = utils.calculate_minimal_box_area(contour)
    assert 100 == area


def test_that_given_angle_in_radians_when_convert_angle_to_degrees_then_angle_is_converted():
    angle_in_radians = (- 3 * math.pi / 4)
    angle_in_degrees = utils.convert_to_degrees(angle_in_radians)
    assert 225.0 == angle_in_degrees
