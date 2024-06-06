import os

from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2.QtWidgets import QVBoxLayout

import maya.cmds as cmds

from ui.main.widgets.rig_widget.modules_widget import ModulesWidget
from controller.rig_build.base_build import BaseBuild

class RigWidget(QtWidgets.QWidget):
    """
    A widget for handling rig-related functionality.
    
    Args:
        c_data (CData): The data object.
        c_component (CComponent): The component object.
        parent (QWidget, optional): The parent widget. Defaults to None.
    """
    closing = QtCore.Signal()

    def __init__(self, c_data, c_component, parent=None):
        super().__init__(parent)

        self.c_data = c_data
        self.c_component = c_component

        self.c_build = BaseBuild(self.c_component)
        self.func_dict = self.c_build.data()

        self.add_widgets()
        self.add_layouts()
        self.add_connections()
        
    def add_widgets(self):

        self.list_widget = QtWidgets.QListWidget()
        self.list_widget.setMaximumHeight(250)
        self.list_widget.setSelectionMode(QtWidgets.QListWidget.NoSelection)

        for key, value in self.func_dict.items():

            list_widget = QtWidgets.QWidget()
            checkbox = QtWidgets.QCheckBox()
            func_label = QtWidgets.QLabel(value['label'])
            run_button = QtWidgets.QPushButton('R')
            open_button = QtWidgets.QPushButton('O')

            checkbox.setChecked(True)

            list_widget_layout = QtWidgets.QHBoxLayout()
            left_side_layout = QtWidgets.QHBoxLayout()
            right_side_layout = QtWidgets.QHBoxLayout()

            list_widget_layout.addLayout(left_side_layout)
            list_widget_layout.addLayout(right_side_layout)
            list_widget_layout.setAlignment(left_side_layout, QtCore.Qt.AlignLeft)
            list_widget_layout.setAlignment(right_side_layout, QtCore.Qt.AlignRight)

            left_side_layout.addWidget(checkbox)
            left_side_layout.addSpacing(20)
            left_side_layout.addWidget(func_label)

            right_side_layout.addWidget(run_button)
            right_side_layout.addWidget(open_button)

            list_widget.setLayout(list_widget_layout)

            list_item = QtWidgets.QListWidgetItem()
            list_item.setSizeHint(list_widget.sizeHint())
            self.list_widget.addItem(list_item)
            self.list_widget.setItemWidget(list_item, list_widget)

            run_button.clicked.connect(value['func'])
            checkbox.stateChanged.connect(lambda state, key=key: self.set_status(key, state))
            if value['tool'] != None:
                open_button.clicked.connect(value['tool'])

        self.run_all_button = QtWidgets.QPushButton('Run All')
        self.run_all_button.clicked.connect(self.run_all)

    def hide_tool_windows_on_close(self):

        self.func_dict['import_blueprint']['tool_hide']()

    def hideEvent(self, event):
        self.closing.emit()
        event.accept()

    def add_layouts(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(QtCore.Qt.AlignTop)
        layout.setContentsMargins(5, 5, 5, 5)
        
        layout.addWidget(self.list_widget)
        layout.addWidget(self.run_all_button)

    def add_connections(self):

        self.closing.connect(self.hide_tool_windows_on_close)
        for widget in self.children():
            if isinstance(widget, QtWidgets.QPushButton):
                widget.clicked.connect(self.update_project_path)

        # self.import_model_button.clicked.connect(self.import_model)
        # self.import_blueprint_button.clicked.connect(self.import_blueprint)
        # self.modules_widget_button.clicked.connect(self.show_modules_widget)

    def set_status(self, key, status):
        """
        Sets the status of the given key.
        
        Args:
            key (str): The key to set the status for.
            status (bool): The status to set.
        """
        self.test_dict[key]['is_checked'] = status
        
    def run_all(self):
        """
        Runs all the functions in the given dictionary.
        
        Args:
            dict (dict): The dictionary of functions to run.
        """
        self.update_project_path()
        for key, value in self.func_dict.items():
            if value['is_checked']:
                value['func']()

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
