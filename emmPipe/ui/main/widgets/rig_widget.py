from PySide2 import QtWidgets
from PySide2.QtWidgets import QVBoxLayout

class RigWidget(QtWidgets.QWidget):
    
        def __init__(self, c_data, parent=None):
            super().__init__(parent)
    
            self.c_data = c_data

            self.add_widgets()
            self.add_layouts()
        
        def add_widgets(self):
            
            self.button = QtWidgets.QPushButton('Rig')

        def add_layouts(self):
            main_layout = QVBoxLayout(self)
            
            main_layout.addWidget(self.button)
        
        def add_connections(self):
            pass