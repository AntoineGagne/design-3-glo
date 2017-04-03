from design.ui.models.world_model import WorldModel
import numpy
import collections


class WorldController:
    def __init__(self, model: WorldModel):
        self.world_model = model

    def update_world_image(self, image: numpy.ndarray):
        self.world_model.game_image = image
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

    def update_real_path(self, coordinates):
        self.world_model.real_path.append(coordinates)
        self.world_model.announce_update()

    def reset_robot_real_path(self):
        self.world_model.real_path = collections.deque(maxlen=100)
        self.world_model.announce_update()

    def update_game_zone_coordinates(self, coordinates):
        self.world_model.game_zone = coordinates
        self.world_model.announce_update()
