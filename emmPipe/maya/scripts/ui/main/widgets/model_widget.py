import os

from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2.QtWidgets import QVBoxLayout

import maya.cmds as cmds

from rig.component import component

class ModelWidget(QtWidgets.QWidget):
    """
    A widget for handling model-related functionality.

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
        """
        Add widgets to the widget layout.
        """
        self.import_button = QtWidgets.QPushButton('Import Model')
        self.open_button = QtWidgets.QPushButton('Open Model')
        self.reference_button = QtWidgets.QPushButton('Reference Model')

    def add_layouts(self):
        """
        Add layouts to the widget.
        """
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        layout.addWidget(self.import_button)
        layout.addWidget(self.open_button)
        layout.addWidget(self.reference_button)

        layout.addStretch()

    def add_connections(self):
        """
        Add signal-slot connections for the widget.
        """
        self.import_button.clicked.connect(self.import_model)
        self.open_button.clicked.connect(self.open_model)
        self.reference_button.clicked.connect(self.reference_model)

    def import_model(self):
        """
        Imports the model component.
        """
        self.c_component.project_path = self.c_data.component_path
        print(self.c_component.project_path)
        self.c_component.import_model_component()

    def open_model(self):
        """
        Opens the model component.
        """
        self.c_component.project_path = self.c_data.component_path
        self.c_component.open_model_component()

    def reference_model(self):
        """
        References the model component.
        """
        self.c_component.project_path = self.c_data.component_path
        self.c_component.reference_model_component()
