import pytest
import design.vision.world_vision as world_vision


@pytest.mark.skip(reason="no way of currently testing this")
def test_that_given_drawing_zone_coordinates_when_calculate_table_orientation_then_table_orientation_is_calculated():
    drawing_zone_coordinates = [(200, 205), (400, 195), (400, 395), (200, 405)]
    drawing_zone_coordinates2 = [(365, 342), (660, 290), (712, 585), (417, 637)]
    assert -2.86 == world_vision.calculate_table_rotation(drawing_zone_coordinates)
    assert -10 == world_vision.calculate_table_rotation(drawing_zone_coordinates2)
