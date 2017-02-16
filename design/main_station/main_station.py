"""
    This is the main base station class
     responsible for instantiating each of the views,
     controllers, and the model (and passing the
     references between them).
     Generally this is very minimal
"""
import sys
from PyQt5.QtWidgets import QApplication
from .models.model import Model
from .controllers.main_controller import MainController
from .views.main_view import MainView


class BaseStation(QApplication):
    def __init__(self, sys_argv):
        super(BaseStation, self).__init__(sys_argv)
        self.model = Model()
        self.main_ctrl = MainController(self.model)
        self.main_view = MainView(self.model, self.main_ctrl)
        self.main_view.show()


if __name__ == '__main__':
    app = BaseStation(sys.argv)
    sys.exit(app.exec_())
