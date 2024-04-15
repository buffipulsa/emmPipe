
from PySide2 import QtWidgets

from ui.ui_utils import maya_main_window, DockableUI



class ModulesWidget(QtWidgets.QDialog):

    WINDOW_TITLE = 'Modules'

    WINDOW_HEIGHT = 400
    WINDOW_WIDTH = 400

    def __init__(self, parent=maya_main_window()):
        super().__init__(parent)

        self.setWindowTitle(self.WINDOW_TITLE)
        self.setGeometry(100, 100, self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
        self.setVisible(True)
        print('ModulesWidget')

    def add_widgets(self):
        pass

    def add_layouts(self):
        pass

    def add_connections(self):
        pass