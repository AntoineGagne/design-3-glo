"""
    This class is a model for visualizing the game
"""
import numpy


class WorldModel:
    def __init__(self):
        self._obstacles_coordinates = None
        self._path_coordinates = None
        self._robot_coordinates = None
        self._robot_real_path = None
        self._drawing_zone_coordinates = None
        self._game_image = None
        self._game_zone_coordinates = None

        self._update_functions = []

    @property
    def robot_real_path(self):
        return self._robot_real_path

    @robot_real_path.setter
    def robot_real_path(self, path: list):
        self._robot_real_path = path

    @property
    def game_zone_coordinates(self):
        return self._game_zone_coordinates

    @game_zone_coordinates.setter
    def game_zone_coordinates(self, coordinates: list):
        self._game_zone_coordinates = coordinates

    @property
    def obstacles_coordinates(self):
        return self._obstacles_coordinates

    @obstacles_coordinates.setter
    def obstacles_coordinates(self, coordinates):
        self._obstacles_coordinates = coordinates

    @property
    def path_coordinates(self):
        return self._path_coordinates

    @path_coordinates.setter
    def path_coordinates(self, coordinates):
        self._path_coordinates = coordinates

    @property
    def robot_coordinates(self):
        return self._robot_coordinates

    @robot_coordinates.setter
    def robot_coordinates(self, coordinates):
        self._robot_coordinates = coordinates

    @property
    def drawing_zone_coordinates(self):
        return self._drawing_zone_coordinates

    @drawing_zone_coordinates.setter
    def drawing_zone_coordinates(self, coordinates):
        self._drawing_zone_coordinates = coordinates

    @property
    def game_image(self):
        return self._game_image

    @game_image.setter
    def game_image(self, image: numpy.ndarray):
        self._game_image = image

    # subscribe a view method for updating
    def subscribe_update_function(self, function):
        if function not in self._update_functions:
            self._update_functions.append(function)

    # unsubscribe a view method for updating
    def unsubscribe_update_function(self, function):
        if function in self._update_functions:
            self._update_functions.remove(function)

    # update registered view methods
    def announce_update(self):
        for function in self._update_functions:
            function()
