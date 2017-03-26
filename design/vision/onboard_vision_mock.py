""" Author: TREMBLAY, Alexandre
Last modified: Febuary 13th, 2017

This module mocks the acquisition of a polygon from
the onboard camera. Very simplistic. """


class OnboardVisionMock():
    """ Mocks onboard vision """

    def __init__(self):
        self.last_capture = None

    def capture(self):
        """ Takes a picture in front of the camera, and picks the one with the relative
        position indicated in the argument """
        self.last_capture = "MOCK.POLYGON"

    def get_captured_vertices(self, zoom, orientation):
        """ Returns mocked polygon's vertices in a list
        Turning the polygon's vertices according to parameter is not supported yet!"""

        with open("mockOnboardVision.txt", "r") as mock:
            vertices = mock.readlines()

        list_of_vertices = []
        for point in vertices:
            current_point = (int(point.split(',')[0][1:]), int(point.split(',')[1][:-2]))
            list_of_vertices.append(current_point)

        return list_of_vertices
