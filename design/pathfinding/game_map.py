""" This module contains a class that acts as stockage for the multiple
game elements and their positions. """

from design.pathfinding.constants import ROBOT_SAFETY_MARGIN
from design.pathfinding.constants import PointOfInterest


ANTENNA_SLIDER_LENGTH = 75
ANTENNA_SLIDER_START_OFFSET_OF_MAP_CORNER = 42


class GameMap():
    """ Contains game map elements """

    def __init__(self):
        """ TEST CASE """

        self.points_of_interest = {}

        self.points_of_interest[PointOfInterest.ANTENNA_STOP_SEARCH_POINT] = (90, 110)
        self.points_of_interest[PointOfInterest.ANTENNA_START_SEARCH_POINT] = (90, 38)
        self.points_of_interest[PointOfInterest.DRAWING_ZONE] = (26, 27)
        self.points_of_interest[PointOfInterest.EXIT_DRAWING_ZONE_AFTER_CYCLE] = [(20, 115), (30, 115), (40, 115),
                                                                                  (50, 115), (60, 115), (70, 115),
                                                                                  (80, 115), (90, 115)]

        self.drawing_zone_side_length = 50

    def set_drawing_zone_borders(self, corners_positions):
        """ Sets the drawing zone's origin and side length value """
        self.points_of_interest[PointOfInterest.DRAWING_ZONE] = corners_positions[0]
        self.drawing_zone_side_length = corners_positions[1][1] - corners_positions[0][1]

    def set_antenna_search_points(self, northeastern_corner):
        """ Sets the antenna's start of search point """
        self.points_of_interest[PointOfInterest.ANTENNA_START_SEARCH_POINT] = (
            northeastern_corner[0] - ROBOT_SAFETY_MARGIN - 3, northeastern_corner[1] + ANTENNA_SLIDER_START_OFFSET_OF_MAP_CORNER)
        self.points_of_interest[PointOfInterest.ANTENNA_STOP_SEARCH_POINT] = (
            northeastern_corner[0] - ROBOT_SAFETY_MARGIN - 3, northeastern_corner[1] + ANTENNA_SLIDER_START_OFFSET_OF_MAP_CORNER + ANTENNA_SLIDER_LENGTH)

    def get_point_of_interest(self, point_of_interest_type):
        """ Returns antenna zone/point """
        return self.points_of_interest.get(point_of_interest_type)
