"""
The controller class does the real logic,
and passes on data to the model
"""

import design.main_station.utils as utils


class WorldController:
    def __init__(self, model):
        self.world_model = model

    def update_world_image(self):
        """
            update model data and announce changes
        """
        self.world_model.game_image = utils.get_latest_created_image()
        self.world_model.announce_update()

    def update_path(self, path):
        self.world_model.path_coordinates = path
        self.world_model.announce_update()

    def update_drawing_zone(self, coordinates):
        self.world_model.drawing_zone_coordinates = coordinates
        self.world_model.announce_update()

    def update_robot_position(self, coordinates):
        self.world_model.robot_coordinates = coordinates
        self.world_model.announce_update()

    def update_obstacles_coordinates(self, coordinates):
        self.world_model.obstacles_coordinates = coordinates
        self.world_model.announce_update()
