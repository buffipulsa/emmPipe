import os

from PySide2 import QtWidgets
from PySide2.QtWidgets import QVBoxLayout

class RigWidget(QtWidgets.QWidget):
    
        def __init__(self, c_data, c_component, parent=None):
            super().__init__(parent)
    
            self.c_data = c_data
            self.c_component = c_component

            self.add_widgets()
            self.add_layouts()

            #self.update_build_script_path()
        
        def add_widgets(self):
            
            self.button = QtWidgets.QPushButton('Build')

        def add_layouts(self):
            main_layout = QVBoxLayout(self)
            
            main_layout.addWidget(self.button)
        
        def add_connections(self):
            
            self.button.clicked.connect(self.print_component_path)

        def print_component_path(self):
            print(self.c_data.component_path)