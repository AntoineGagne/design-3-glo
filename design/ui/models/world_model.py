class WorldModel:
    def __init__(self):
        self.obstacles_coordinates = None
        self.calculated_path = None
        self.robot_coordinates = None
        self.real_path = []
        self.drawing_zone_coordinates = None
        self.game_image = None
        self.game_zone_coordinates = None
        self.base_obstacles_coordinates = None
        self.base_robot_coordinates = None
        self._update_functions = []

    def subscribe_update_function(self, function):
        if function not in self._update_functions:
            self._update_functions.append(function)

    def unsubscribe_update_function(self, function):
        if function in self._update_functions:
            self._update_functions.remove(function)

    def announce_update(self):
        for function in self._update_functions:
            function()
