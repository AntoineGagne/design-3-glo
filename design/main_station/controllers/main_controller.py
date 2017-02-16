"""
The controller class does the real logic,
and passes on data to the model
"""


class MainController:

    def __init__(self, model):
        self.model = model

    def update_lcd_display(self, value):
        """
            update model data and announce changes
        """
        self.model.timer = value
        self.model.announce_update()
