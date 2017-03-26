""" This module contains a class relative to mutable positions, i.e
the robot's position """


class MutablePosition():
    """ Manages mutable positions """

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def move(self, dx, dy):
        """ Adds dx, dy movement to position """
        self.x = self.x + dx
        self.y = self.y + dy

    def to_tuple(self):
        """ Returns immutable tuple of the current position """
        return (self.x, self.y)

    def __str__(self):
        return "({0}, {1})".format(self.x, self.y)
