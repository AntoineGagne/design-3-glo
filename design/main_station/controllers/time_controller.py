"""
The controller class does the real logic,
and passes on data to the model
"""


class TimeController:

    def __init__(self, model):
        self.time_model = model

    def update_lcd_display(self, value):
        """
            update model data and announce changes
        """
        self.time_model.timer = value
        self.time_model.announce_update()
