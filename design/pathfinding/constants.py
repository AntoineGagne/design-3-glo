""" Author: TREMBLAY, Alexandre
Last modified: Febuary 7th, 2017

This module contains relevant constants and enumerations for the pathfinding subpackage """

from enum import Enum

TRANSLATION_THRESHOLD = 1  # cm
ROTATION_THRESHOLD = 0.5  # degree(s)
TRANSLATION_SPEED = 3  # cm/s
ROTATION_SPEED = 20  # degree(s) per second


class PointOfInterest(Enum):
    """ Enumeration that allows naming of multiple points or zones of interest """
    FIGURE_ZONE = "FGR_ZONE"
    ANTENNA_START_SEARCH_POINT = "ANT_START_SEARCH_PT"
    ANTENNA_STOP_SEARCH_POINT = "ANT_STOP_SEARCH_PT"
    DRAWING_ZONE = "DRW_ZONE"


class FigureOrdering(Enum):
    """ Enumeration that allows arbitrary ordering of figure independetly of their
    real position """

    LEFTMOST = 0
    INNER_LEFT = 1
    INNER_RIGHT = 2
    RIGHTMOST = 3


class FigureFieldOfViewArea(Enum):
    """ Enumeration that allows the robot to find in what field of view general area
    they can find the figure """

    FIGURE_0 = (190, FigureOrdering.LEFTMOST)
    FIGURE_1 = (190, FigureOrdering.RIGHTMOST)
    FIGURE_2 = (90, FigureOrdering.LEFTMOST)
    FIGURE_3 = (90, FigureOrdering.INNER_LEFT)
    FIGURE_4 = (90, FigureOrdering.INNER_RIGHT)
    FIGURE_5 = (90, FigureOrdering.RIGHTMOST)
    FIGURE_6 = (-10, FigureOrdering.LEFTMOST)
    FIGURE_7 = (-10, FigureOrdering.RIGHTMOST)
