""" This module contains relevant constants and enumerations for the pathfinding subpackage """

from enum import Enum


TRANSLATION_THRESHOLD = 1.5  # cm
ROTATION_THRESHOLD = 0.25  # degree(s)
TRANSLATION_SPEED = 5  # cm/s
ROTATION_SPEED = 3  # degree(s) per second
STANDARD_HEADING = 90  # degrees
TABLE_X = 111
TABLE_Y = 230
OBSTACLE_RADIUS = 7
ROBOT_SAFETY_MARGIN = 16
DEVIATION_THRESHOLD = 1

GRAPH_GRID_WIDTH = 1    # Should be between 1 and 3 cm
MAXIMUM_GRID_NODE_HEIGHT = 30


class TranslationStatus(Enum):
    """ Translation status enumeration of visual servo management """
    MOVING = "MOVING"
    CORRECTING_HEADING = "CORRECTING_HEADING"
    CORRECTING_POSITION = "CORRECTING_POSITION"


class RotationStatus(Enum):
    """ Rotation status enumeration of visual servo management """
    ROTATING = "ROTATING"
    CORRECTING_POSITION = "CORRECTION_POSITION"
    CORRECTING_HEADING = "CORRECTING_HEADING"


class PointOfInterest(Enum):
    """ Enumeration that allows naming of multiple points or zones of interest """
    EXIT_DRAWING_ZONE_AFTER_CYCLE = "EXIT_DRW_ZONE"
    ANTENNA_START_SEARCH_POINT = "ANT_START_SEARCH_PT"
    ANTENNA_STOP_SEARCH_POINT = "ANT_STOP_SEARCH_PT"
    DRAWING_ZONE = "DRW_ZONE"
