"""
    This class is a model for visualizing the game
"""


class WorldModel:
    def __init__(self):
        self._obstacles_coords = []
        self._path_coords = []
        self._robot_coords = []
        self._drawing_zone_coords = [(0, 342), (13, 19), (21, 32), (44, 56), (93, 83), (0, 342)]   # dummy test
        self._game_image = ""

        # these will be the registered functions for view updating
        self._update_funcs = []

    @property
    def obstacles_coords(self):
        return self._obstacles_coords

    @obstacles_coords.setter
    def obstacles_coords(self, coordinates):
        self._obstacles_coords = coordinates

    @property
    def path_coords(self):
        return self._path_coords

    @path_coords.setter
    def path_coords(self, coordinates):
        self._path_coords = coordinates

    @property
    def robot_coords(self):
        return self._robot_coords

    @robot_coords.setter
    def robot_coords(self, coordinates):
        self._robot_coords = coordinates

    @property
    def drawing_zone_coords(self):
        return self._drawing_zone_coords

    @drawing_zone_coords.setter
    def drawing_zone_coords(self, coordinates):
        self._drawing_zone_coords = coordinates

    @property
    def game_image(self):
        return self._game_image

    @game_image.setter
    def game_image(self, image_path):
        self._game_image = image_path

    # subscribe a view method for updating
    def subscribe_update_func(self, func):
        if func not in self._update_funcs:
            self._update_funcs.append(func)

    # unsubscribe a view method for updating
    def unsubscribe_update_func(self, func):
        if func in self._update_funcs:
            self._update_funcs.remove(func)

    # update registered view methods
    def announce_update(self):
        for func in self._update_funcs:
            func()
