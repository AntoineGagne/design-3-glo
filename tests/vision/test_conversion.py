from design.vision.conversion import (calculate_table_rotation,
                                      set_top_left_world_game_zone_coordinate)
from design.vision.world_utils import calculate_norm


def test_that_given_coordinates_when_calculate_top_left_world_game_zone_coordinate_then_coordinate_is_calculated():
    table_angle = 10.0
    top_left_drawing_zone = (0, 0)
    top_left_table = set_top_left_world_game_zone_coordinate(top_left_drawing_zone, table_angle)
    assert calculate_norm(-29.6, -20.9, top_left_table[0], top_left_table[1]) < 1


def test_that_given_drawing_zone_coordinates_when_calculate_table_angle_then_table_angle_is_calculated():
    drawing_zone_coordinates = [(200, 205), (400, 195), (400, 395), (200, 405)]
    drawing_zone_coordinates2 = [(365, 342), (660, 290), (712, 585), (417, 637)]
    assert -2.86 == calculate_table_rotation(drawing_zone_coordinates)
    assert -10 == calculate_table_rotation(drawing_zone_coordinates2)
