from design.ui.models.world_model import WorldModel
import numpy

from design.vision.world_utils import calculate_norm


class WorldController:
    def __init__(self, model: WorldModel):
        self.world_model = model

    def update_world_image(self, image: numpy.ndarray):
        self.world_model.game_image = image
        self.world_model.announce_update()

    def update_path(self, path):
        self.world_model.calculated_path.extend(path)
        self.world_model.announce_update()

    def update_drawing_zone(self, coordinates):
        self.world_model.drawing_zone_coordinates = coordinates

    def update_robot_position(self, coordinates, base_coordinates):
        self.world_model.robot_coordinates = coordinates
        self.world_model.base_robot_coordinates = base_coordinates

    def update_obstacles_coordinates(self, coordinates, base_coordinates):
        self.world_model.obstacles_coordinates = coordinates
        self.world_model.base_obstacles_coordinates = base_coordinates

    def update_real_path(self, coordinates):
        if self.world_model.real_path:
            if calculate_norm(self.world_model.real_path[-1][0],
                              self.world_model.real_path[-1][1],
                              coordinates[0],
                              coordinates[1]) > 50:
                self.world_model.real_path.append(coordinates)
        else:
            self.world_model.real_path.append(coordinates)

    def reset_paths(self):
        self.world_model.real_path = []
        self.world_model.calculated_path = []
        self.world_model.announce_update()

    def update_game_zone_coordinates(self, coordinates):
        self.world_model.game_zone = coordinates
