class MainModel:
    def __init__(self):
        self.time = 0
        self.timer_is_on = False
        self.start_new_cycle = False
        self.find_robot_flag = False
        self.log_messages = ""

        self._update_functions = []

    def subscribe_update_function(self, function):
        if function not in self._update_functions:
            self._update_functions.append(function)

    def unsubscribe_update_function(self, function):
        if function in self._update_functions:
            self._update_functions.remove(function)

    def announce_update(self):
        for function in self._update_functions:
            function()
