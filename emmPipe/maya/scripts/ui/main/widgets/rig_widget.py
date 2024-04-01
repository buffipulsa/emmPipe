import os

from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2.QtWidgets import QVBoxLayout

import maya.cmds as cmds

from ui.main.widgets.osseousWidget import OsseousWidget

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
        
    def add_widgets(self):
        
        self.osseous_widget = OsseousWidget()

        self.build_button = QtWidgets.QPushButton('Build')

    def add_layouts(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(QtCore.Qt.AlignTop)
        layout.setContentsMargins(0, 0, 0, 0)
        
        layout.addWidget(self.osseous_widget)
        layout.addWidget(self.build_button)

    def add_connections(self):
        pass

    def update_build_script_path(self):
        self.c_data.build_scripts_path = os.path.join(self.c_data.asset, 'python', 'rigBuild', 'build.py')