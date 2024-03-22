import os

from PySide2 import QtWidgets
from PySide2.QtWidgets import QVBoxLayout

import maya.cmds as cmds

from emmPipe.ui.main.widgets.osseousWidget import OsseousWidget

class RigWidget(QtWidgets.QWidget):
    
        def __init__(self, c_data, c_component, parent=None):
            super().__init__(parent)
    
            self.c_data = c_data
            self.c_component = c_component

            self.add_widgets()
            self.add_layouts()

            #self.update_build_script_path()
        
        def add_widgets(self):
            
            self.osseous_widget = OsseousWidget()

            self.build_button = QtWidgets.QPushButton('Build')

        def add_layouts(self):
            main_layout = QVBoxLayout(self)
            main_layout.setContentsMargins(0, 0, 0, 0)
            
            main_layout.addWidget(self.osseous_widget)
            main_layout.addWidget(self.build_button)

        def add_connections(self):
            pass

        def update_build_script_path(self):
            self.c_data.build_scripts_path = os.path.join(self.c_data.asset, 'python', 'rigBuild', 'build.py')