from PyQt5 import QtGui


class MainController(object):

    def __init__(self, model):
        self.model = model

    # called from view class
    def start(self, checked):
        # put control logic here
        self.model.start = checked
        self.model.announce_update()
