"""
The controller class does the real logic,
and passes on data to the model
"""


class MainController:
    def __init__(self, model):
        self.model = model

    def reset_timer(self):
        self.model.time = 0
        self.model.announce_update()

    def is_timer_on(self):
        return self.model.timer_is_on

    def activate_timer(self):
        self.model.timer_is_on = True
        self.model.announce_update()

    def deactivate_timer(self):
        self.model.timer_is_on = False
        self.model.announce_update()

    def update_time(self):
        self.model.time += 1
        self.model.announce_update()
