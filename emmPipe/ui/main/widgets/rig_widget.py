import os

from PySide2 import QtWidgets
from PySide2.QtWidgets import QVBoxLayout

class RigWidget(QtWidgets.QWidget):
    """
    A widget for handling rig-related functionality.
    
    Args:
        c_data (CData): The data object.
        c_component (CComponent): The component object.
        parent (QWidget, optional): The parent widget. Defaults to None.
    """
    
    def __init__(self, c_data, c_component, parent=None):
        super().__init__(parent)

        self.c_data = c_data
        self.c_component = c_component

        self.add_widgets()
        self.add_layouts()

        #self.update_build_script_path()
    
    def add_widgets(self):
        """
        Add widgets to the widget layout.
        """
        self.button = QtWidgets.QPushButton('Build')

    def add_layouts(self):
        """
        Add layouts to the widget.
        """
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.button)
    
    def add_connections(self):
        """
        Add signal-slot connections for the widget.
        """
        pass

