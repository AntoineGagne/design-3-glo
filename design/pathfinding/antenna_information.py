""" Author: TREMBLAY, Alexandre
Last modified: Febuary 13th, 2017

Modules allow stockage of recieved info from Manchester code
for ulterior use """


class AntennaInformation():
    """ Allows stockage of recieved info from Manchester code """

    def __init__(self):
        self.painting_number = 0
        self.zoom = 1
        self.orientation = 90

    def set_information(self, info_tuple):
        """ Initializes information """

        self.painting_number = int(info_tuple[0])
        self.zoom = int(info_tuple[1])
        self.orientation = int(info_tuple[2])

    def get_painting_number(self):
        """ Returns which painting must be captured """
        return self.painting_number

    def get_drawing_information(self):
        """ Returns zoom and orientation of painting """
        return (self.zoom, self.orientation)
