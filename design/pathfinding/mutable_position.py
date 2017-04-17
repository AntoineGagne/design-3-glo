""" This module contains a class relative to mutable positions, i.e
the robot's position """


class MutablePosition():

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def move(self, dx, dy):
        self.x = self.x + dx
        self.y = self.y + dy

    def to_tuple(self):
        return (self.x, self.y)

    def __str__(self):
        return "({0}, {1})".format(self.x, self.y)
