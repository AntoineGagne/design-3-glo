""" This module contains custom exception types for the pathfinding
subpackage """


class CheckpointNotAccessibleError(Exception):
    """ This exception is raised when an attempt to generate a path
    towards a certain position (the checkpoint) fails. """

    def __init__(self, message):
        super(CheckpointNotAccessibleError, self).__init__()
        self.message = message
