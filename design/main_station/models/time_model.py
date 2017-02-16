class TimeModel:
    def __init__(self):
        self._timer = 0

        # these will be the registered functions for view updating
        self._update_funcs = []

    @property
    def timer(self):
        return self._timer

    @timer.setter
    def timer(self, value):
        self._timer = value

    # subscribe a view method for updating
    def subscribe_update_func(self, func):
        if func not in self._update_funcs:
            self._update_funcs.append(func)

    # unsubscribe a view method for updating
    def unsubscribe_update_func(self, func):
        if func in self._update_funcs:
            self._update_funcs.remove(func)

    # update registered view methods
    def announce_update(self):
        for func in self._update_funcs:
            func()
