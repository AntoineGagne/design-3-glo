class MainModel:
    def __init__(self):
        self.time = 0
        self.timer_is_on = False

        # these will be the registered functions for view updating
        self._update_functions = []

    # subscribe a view method for updating
    def subscribe_update_function(self, function):
        if function not in self._update_functions:
            self._update_functions.append(function)

    # unsubscribe a view method for updating
    def unsubscribe_update_function(self, function):
        if function in self._update_functions:
            self._update_functions.remove(function)

    # update registered view methods
    def announce_update(self):
        for function in self._update_functions:
            function()
