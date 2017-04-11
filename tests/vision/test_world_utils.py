import math
import design.vision.world_utils as utils
import numpy


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
    new_array = (utils.eliminate_duplicated_points(array, minimal_distance))
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


def test_that_given_obstacles_information_when_comparing_then_information_is_similar():
    information1 = [[[879, 428], 'O'], [[1146, 819], 'S'], [[1407, 435], 'N']]
    information2 = [[[880, 430], 'O'], [[1150, 820], 'S'], [[1410, 432], 'N']]
    assert utils.are_obstacles_information_similar(information1,
                                                   information2)


def test_that_given_obstacles_information_when_comparing_then_information_is_not_similar():
    information1 = [[[500, 428], 'O'], [[1146, 819], 'S'], [[1407, 435], 'N']]
    information2 = [[[880, 430], 'O'], [[1150, 820], 'S'], [[1410, 432], 'N']]
    information3 = [[[880, 430], 'O'], [[1150, 820], 'N']]
    assert not utils.are_obstacles_information_similar(information1,
                                                       information2)
    assert not utils.are_obstacles_information_similar(information1,
                                                       information3)
    assert not utils.are_obstacles_information_similar(information2,
                                                       information3)


def test_that_given_drawing_zone_information_when_comparing_then_information_is_similar():
    information1 = [(412, 414), (200, 395), (244, 500), (123, 372)]
    information2 = [(413, 415), (203, 396), (245, 505), (125, 375)]
    assert utils.are_drawing_zone_information_similar(information1,
                                                      information2)


def test_that_given_drawing_zone_information_when_comparing_then_information_is_not_similar():
    information1 = [(412, 414), (200, 395), (244, 500), (123, 372)]
    information2 = [(413, 415), (203, 396), (245, 600), (125, 375)]
    assert not utils.are_drawing_zone_information_similar(information1,
                                                          information2)


def test_that_given_two_robot_information_when_comparing_then_they_are_similar():
    information1 = [(123, 123), 123.00]
    information2 = [(124, 127), 124.00]
    assert utils.are_robot_information_similar(information1, information2)


def test_that_given_two_robot_information_when_comparing_then_they_are_not_similar():
    information1 = [(150, 123), 123.00]
    information2 = [(124, 200), 124.00]
    information3 = [(124, 400), 124.00]
    information4 = [(124, 400), 150.00]
    assert not utils.are_robot_information_similar(information1, information2)
    assert not utils.are_robot_information_similar(information1, information3)
    assert not utils.are_robot_information_similar(information2, information3)
    assert not utils.are_robot_information_similar(information4, information3)


def test_that_given_list_of_obstacles_information_when_comparing_them_then_best_information_is_given():
    obstacles_information = [[[[499, 432], 'O'], [[1150, 820], 'S'], [[1407, 435], 'N']],
                             [[[500, 428], 'O'], [[1146, 819], 'S']],
                             [[[505, 428], 'O'], [[1143, 819], 'S'], [[1402, 436], 'N']],
                             [[[501, 428], 'O'], [[1146, 818], 'S'], [[1407, 435], 'N']],
                             [[[1145, 815], 'S'], [[1405, 433], 'N']],
                             [[[503, 428], 'O'], [[1147, 818], 'S'], [[1406, 432], 'N']]]
    new_information = utils.get_best_information(obstacles_information)
    assert new_information == [[[499, 432], 'O'], [[1150, 820], 'S'], [[1407, 435], 'N']]


def test_that_given_list_of_drawing_zone_information_when_comparing_them_then_best_information_is_given():
    drawing_zone_information = [[(412, 414), (200, 395), (244, 500), (123, 372)],
                                [(413, 415), (203, 396), (245, 505), (125, 375)],
                                [(412, 415), (202, 395), (244, 504), (122, 375)]]
    new_information = utils.get_best_information(drawing_zone_information)
    assert new_information == [(412, 414), (200, 395), (244, 500), (123, 372)]


def test_that_given_list_of_robot_information_when_comparing_them_then_best_information_is_given():
    robot_information = [[(124, 127), 124.00],
                         [(124, 125), 125.10],
                         [(125, 126), 122.00],
                         [(100, 127), 124.00]]
    new_information = utils.get_best_information(robot_information)
    assert new_information == [(124, 127), 124.00]


def test_that_given_two_items_information_when_comparing_then_they_are_similar():
    information1 = [(412, 414), (200, 395), (244, 500), (123, 372)]
    information2 = [(413, 415), (203, 396), (245, 505), (125, 375)]
    information3 = [[[879, 428], 'O'], [[1146, 819], 'S'], [[1407, 435], 'N']]
    information4 = [[[880, 430], 'O'], [[1150, 820], 'S'], [[1410, 432], 'N']]
    information5 = [(123, 123), 123.00]
    information6 = [(124, 127), 124.00]
    assert utils.check_if_both_information_are_similar(information1,
                                                       information2)
    assert utils.check_if_both_information_are_similar(information3,
                                                       information4)
    assert utils.check_if_both_information_are_similar(information5,
                                                       information6)
    assert utils.check_if_both_information_are_similar(information1,
                                                       information1)
    assert utils.check_if_both_information_are_similar(information2,
                                                       information2)
    assert utils.check_if_both_information_are_similar(information3,
                                                       information3)
    assert utils.check_if_both_information_are_similar(information4,
                                                       information4)
    assert utils.check_if_both_information_are_similar(information5,
                                                       information5)
    assert utils.check_if_both_information_are_similar(information6,
                                                       information6)


def test_that_given_two_items_information_when_comparing_then_they_are_not_similar():
    information1 = [(412, 414), (200, 395), (244, 500), (123, 372)]
    information2 = [(413, 415), (203, 396), (245, 600), (125, 375)]
    information3 = [[[500, 428], 'O'], [[1146, 819], 'S'], [[1407, 435], 'N']]
    information4 = [[[880, 430], 'O'], [[1150, 820], 'S'], [[1410, 432], 'N']]
    information5 = [[[880, 430], 'O'], [[1150, 820], 'N']]
    information6 = [(124, 400), 124.00]
    information7 = [(124, 400), 150.00]
    assert not utils.check_if_both_information_are_similar(information1,
                                                           information2)
    assert not utils.check_if_both_information_are_similar(information3,
                                                           information4)
    assert not utils.check_if_both_information_are_similar(information3,
                                                           information5)
    assert not utils.check_if_both_information_are_similar(information4,
                                                           information5)
    assert not utils.check_if_both_information_are_similar(information6,
                                                           information7)


def test_that_given_close_points_in_list_when_eliminate_close_points_then_they_are_eliminated():
    circles = [(1018, 497), (1018, 497)]
    assert [[1018, 497]] == utils.eliminate_close_points_in_list(circles, 200)
