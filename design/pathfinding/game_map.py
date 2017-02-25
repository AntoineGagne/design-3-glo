""" Author: TREMBLAY, Alexandre
Last modified: Febuary 7th, 2017

This module contains a class that acts as stockage for the multiple
game elements and their positions. """

from design.pathfinding.constants import PointOfInterest


class GameMap():
    """ Contains game map elements """

    def __init__(self):
        """ TEST CASE """

        self.points_of_interest = {}

        self.points_of_interest[PointOfInterest.ANTENNA_STOP_SEARCH_POINT] = (100, 92)
        self.points_of_interest[PointOfInterest.ANTENNA_START_SEARCH_POINT] = (100, 42)
        self.points_of_interest[PointOfInterest.DRAWING_ZONE] = (50, 50)
        self.points_of_interest[PointOfInterest.FIGURE_ZONE] = (70, 200)

    def parse(self, telemetry_data):
        """ Parses data recieved by telemetry - TEMPORARY, NO SPLITS IN NON-MOCK -> SERIALIZED
        object will be used """

        print("Starting to parse game map with telemetry = {0}".format(
            telemetry_data))

        print("Game map parsing finished")

    def get_point_of_interest(self, point_of_interest_type):
        """ Returns antenna zone/point """
        return self.points_of_interest.get(point_of_interest_type)
