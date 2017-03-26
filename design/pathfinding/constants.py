""" This module contains relevant constants and enumerations for the pathfinding subpackage """

from enum import Enum

TRANSLATION_THRESHOLD = 0.50  # cm
ROTATION_THRESHOLD = 0.25  # degree(s)
TRANSLATION_SPEED = 5  # cm/s
ROTATION_SPEED = 10  # degree(s) per second
STANDARD_HEADING = 90  # degrees
TABLE_X = 111
TABLE_Y = 230
OBSTACLE_RADIUS = 7
ROBOT_SAFETY_MARGIN = 16


class PointOfInterest(Enum):
    """ Enumeration that allows naming of multiple points or zones of interest """
    EXIT_DRAWING_ZONE_AFTER_CYCLE = "EXIT_DRW_ZONE"
    ANTENNA_START_SEARCH_POINT = "ANT_START_SEARCH_PT"
    ANTENNA_STOP_SEARCH_POINT = "ANT_STOP_SEARCH_PT"
    DRAWING_ZONE = "DRW_ZONE"
