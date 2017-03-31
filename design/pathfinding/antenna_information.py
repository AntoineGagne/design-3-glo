""" Modules allow stockage of recieved info from Manchester code
for ulterior use """


class AntennaInformation():
    """ Allows stockage of recieved info from Manchester code """

    def __init__(self):
        self.painting_number = 0
        self.zoom = 1
        self.orientation = 90
        self.strength_curve = {}

        print("AntennaInformationConstructorCalled")
