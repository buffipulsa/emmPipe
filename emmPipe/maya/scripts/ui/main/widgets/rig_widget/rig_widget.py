import os

from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2.QtWidgets import QVBoxLayout

import maya.cmds as cmds

from ui.main.widgets.osseousWidget import OsseousWidget
from ui.main.widgets.rig_widget.modules_widget import ModulesWidget

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
        
        self.import_model_button = QtWidgets.QPushButton('Import Model')
        self.import_blueprint_button = QtWidgets.QPushButton('Import Blueprint')

        self.modules_widget_button = QtWidgets.QPushButton('Modules')

        # self.module_widget = ModulesWidget(self.parent())

    def add_layouts(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(QtCore.Qt.AlignTop)
        layout.setContentsMargins(0, 0, 0, 0)
        
        layout.addWidget(self.import_model_button)
        layout.addWidget(self.import_blueprint_button)
        layout.addWidget(self.modules_widget_button)
        #layout.addWidget(self.osseous_widget)

    def add_connections(self):

        for widget in self.children():
            if isinstance(widget, QtWidgets.QPushButton):
                widget.clicked.connect(self.update_project_path)

        self.import_model_button.clicked.connect(self.import_model)
        self.import_blueprint_button.clicked.connect(self.import_blueprint)
        self.modules_widget_button.clicked.connect(self.show_modules_widget)

    def update_project_path(self):
        self.c_component.project_path = self.c_data.component_path

    def update_build_script_path(self):
        self.c_data.build_scripts_path = os.path.join(self.c_data.asset, 'python', 'rigBuild', 'build.py')

    def import_model(self):
        """
        Imports the model component.
        """
        self.c_component.import_model_component()

    def import_blueprint(self):
        """
        Imports the blueprint component.
        """
        self.c_component.import_blueprint_component()

    def show_modules_widget(self):

        try:
            self.module_widget.close()
            self.module_widget.deleteLater()
        except:
            pass
        self.module_widget = ModulesWidget(self)
        self.module_widget.show()
