import os

from PySide2 import QtWidgets
from PySide2.QtWidgets import QVBoxLayout, QHBoxLayout
from PySide2.QtCore import Qt

import maya.cmds as cmds

from emmPipe.ui.ui_utils import CollapsibleWidget

class OsseousWidget(QtWidgets.QWidget):
    
        def __init__(self, parent=None):
            super().__init__(parent)

            self.add_widgets()
            self.add_layouts()
            self.add_connections()
        
        def add_widgets(self):
            
            self.osseous_widget = CollapsibleWidget('Osseous')

            self.test_button = QtWidgets.QPushButton('+')
            self.test_button.setFixedWidth(20)

        def add_layouts(self):
            self.main_layout = QVBoxLayout(self)
            self.main_layout.setContentsMargins(0, 0, 0, 0)

            self.osseous_widget.body_layout.addWidget(self.test_button)

            self.main_layout.addWidget(self.osseous_widget)

        def add_connections(self):
            
            self.test_button.clicked.connect(self.create_test)

        def create_test(self):
            layout = QHBoxLayout()
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setAlignment(Qt.AlignLeft)

            line_edit = QtWidgets.QLineEdit('Test')
            line_edit.setContentsMargins(10,2,10,2)
            line_edit.setPlaceholderText('Enter text here')
            line_edit.setFixedWidth(70)

            combo_box = QtWidgets.QComboBox()
            combo_box.setFixedWidth(40)
            combo_box.addItem('C')
            combo_box.addItem('L')
            combo_box.addItem('R')

            line_edit2 = QtWidgets.QLineEdit('#')
            line_edit2.setFixedWidth(30)

            combo_box2 = QtWidgets.QComboBox()
            combo_box2.setFixedWidth(60)

            layout.addWidget(line_edit)
            layout.addWidget(combo_box)
            layout.addWidget(line_edit2)
            layout.addWidget(combo_box2)
            
            self.osseous_widget.body_layout.addLayout(layout)


        

