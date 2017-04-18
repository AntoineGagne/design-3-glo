from design.ui.models.painting_model import PaintingModel
import numpy


class PaintingController:
    def __init__(self, model: PaintingModel):
        self.model = model

    def update_painting_image(self, image: numpy.ndarray):
        self.model.painting_image = image
        self.model.announce_update()
