from design.ui.models.main_model import MainModel


class MainController:
    def __init__(self, model: MainModel):
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

    def start_new_cycle(self):
        self.model.start_new_cycle = True
        self.model.announce_update()

    def update_console_log(self, new_message: str):
        self.model.log_messages += "{}\n".format(new_message)
        self.model.announce_update()

    def find_robot(self):
        self.model.find_robot_flag = True
        self.model.announce_update()
