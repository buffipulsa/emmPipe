import os

from PySide2 import QtWidgets
from PySide2.QtWidgets import QVBoxLayout

import maya.cmds as cmds

from emmPipe.rig.component import component

class ModelWidget(QtWidgets.QWidget):
    
        def __init__(self, c_data, c_component, parent=None):
            super().__init__(parent)

            self.c_data = c_data
            self.c_component = c_component

            self.add_widgets()
            self.add_layouts()
        
        def add_widgets(self):
            
            self.import_button = QtWidgets.QPushButton('Import Model')
            self.open_button = QtWidgets.QPushButton('Open Model')
            self.reference_button = QtWidgets.QPushButton('Reference Model')

        def add_layouts(self):
            main_layout = QVBoxLayout(self)
            
            main_layout.addWidget(self.import_button)
            main_layout.addWidget(self.open_button)
            main_layout.addWidget(self.reference_button)
        
        def add_connections(self):
            self.import_button.clicked.connect(self.import_model)
            self.open_button.clicked.connect(self.open_model)
            self.reference_button.clicked.connect(self.reference_model)
        
        def import_model(self):
            self.c_component.project_path = self.c_data.component_path
            self.c_component.import_model_component()
        
        def open_model(self):
            self.c_component.project_path = self.c_data.component_path
            self.c_component.open_model_component()

        def reference_model(self):
            self.c_component.project_path = self.c_data.component_path
            self.c_component.import_model_component()