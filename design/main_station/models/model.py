from PyQt5 import QtGui
"""
    The model class basically just holds a
    bunch of data variables and some minimal
    logic for exposing and announcing changes
    to this data.
"""


class Model(object):
    def __init__(self):
        self._update_funcs = []

        # variable placeholders
        self.start = False

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
