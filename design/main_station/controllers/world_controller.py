"""
The controller class does the real logic,
and passes on data to the model
"""

import design.main_station.utils as utils

# self._obstacles_coords = []
# self._path_coords = []
# self._robot_coords = []
# self._drawing_zone_coords = []
# self._game_image = ""


class WorldController:

    def __init__(self, model):
        self.world_model = model

    # called from view class
    def change_running(self, checked):
        # put control logic here
        self.model.running = checked
        self.model.announce_update()

    def update_world_image(self):
        """
            update model data and announce changes
        """
        self.world_model.game_image = utils.get_latest_image()
        self.world_model.announce_update()

    def update_path(self, path):
        self.world_model.path_coords = path
        self.world_model.announce_update()
