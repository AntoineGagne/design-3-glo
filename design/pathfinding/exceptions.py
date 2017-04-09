""" This module contains custom exception types for the pathfinding
subpackage """


class CheckpointNotAccessibleError(Exception):
    """ This exception is raised when an attempt to generate a path
    towards a certain position (the checkpoint) fails. """

    def __init__(self, message):
        super(CheckpointNotAccessibleError, self).__init__()
        self.message = message


class OutOfRetriesForCaptureError(Exception):
    """ This exception is raised when there are no more capture retry vectors
    to do. """

    def __init__(self, message):
        super(OutOfRetriesForCaptureError, self).__init__()
        self.message = message
