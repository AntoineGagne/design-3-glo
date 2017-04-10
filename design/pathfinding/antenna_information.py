""" Modules allow stockage of recieved info from Manchester code
for ulterior use """
from collections import defaultdict


class AntennaInformation():
    """ Allows stockage of recieved info from Manchester code """

    def __init__(self):
        self.painting_number = 0
        self.zoom = 1
        self.orientation = 90
        self.strength_curve = defaultdict(lambda: 0)

        print("AntennaInformationConstructorCalled")

    def __str__(self):
        return "Painting number: {0} Zoom: {1} Orientation: {2}".format(self.painting_number, self.zoom,
                                                                        self.orientation)
