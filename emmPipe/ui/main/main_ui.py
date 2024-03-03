
from PySide2 import QtWidgets

from emmPipe.ui.utils import maya_main_window

class MainUI(QtWidgets.QWidget):

    def __init__(self, parent=maya_main_window()):
        super().__init__(parent)