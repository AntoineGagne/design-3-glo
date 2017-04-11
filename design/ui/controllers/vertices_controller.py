from design.ui.models.vertices_model import VerticesModel


class VerticesController:
    def __init__(self, model: VerticesModel):
        self.model = model

    def update_path(self, path):
        self.model.painting_vertices = path
        self.model.announce_update()
