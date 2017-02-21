from design.chronograph.chronograph import Chronograph


class MainModel:
    def __init__(self):
        self._chronograph = Chronograph()
        self._chronograph_activated = False

        # these will be the registered functions for view updating
        self._update_funcs = []

    @property
    def chronograph(self):
        return self._chronograph

    @property
    def chronograph_activated(self):
        return self._chronograph_activated

    @chronograph_activated.setter
    def chronograph_activated(self, boolean):
        self._chronograph_activated = boolean

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
