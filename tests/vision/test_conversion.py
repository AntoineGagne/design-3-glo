import pytest
from design.vision.conversion import calculate_angle


@pytest.mark.skip(reason="no way of currently testing this")
def test_that_given_drawing_zone_coordinates_when_calculate_table_angle_then_table_angle_is_calculated():
    drawing_zone_coordinates = [(365, 342), (660, 290), (712, 585), (417, 637)]
    assert -10 == calculate_angle(drawing_zone_coordinates)
