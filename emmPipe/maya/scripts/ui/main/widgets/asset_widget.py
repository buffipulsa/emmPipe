import os

from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2.QtWidgets import QVBoxLayout, QHBoxLayout, QStackedWidget, QFileSystemModel
from PySide2.QtWidgets import QTabWidget, QTabBar
from PySide2.QtCore import QStringListModel, QModelIndex

from ui.ui_utils import InfoButtonWidget
from rig.component.component import Component
from ui.ui_path_model import UIPathModel

class AssetWidget(QtWidgets.QWidget):
    """
    A widget for displaying and interacting with asset information.

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

        self.show_cbox.setCurrentText('common')
        self.on_show_changed()

    def add_widgets(self):
        """
        Add widgets to the widget layout.
        """
        self.info_button = InfoButtonWidget(self, 'Here you can select the show and asset you wish to work on.')

        self.show_label = QtWidgets.QLabel('Show:')
        self.asset_label = QtWidgets.QLabel('Asset:')

        self.show_label.setIndent(5)
        self.asset_label.setIndent(25)

        self.show_cbox = QtWidgets.QComboBox()
        self.asset_cbox = QtWidgets.QComboBox()

        self.c_show_model = UIPathModel(os.environ['EMMPIPE_PROJECTS_PATH'])

        self.show_cbox.setModel(self.c_show_model)
        self.asset_cbox.setModel(self.c_data)

        self.show_cbox.setCurrentText('Select Show')

        self.browse_components_button = QtWidgets.QPushButton('Browse Components')

    def add_layouts(self):
        """
        Add layouts to the widget.
        """
        layout = QVBoxLayout(self, alignment=QtCore.Qt.AlignTop)

        label_layout = QHBoxLayout()

        label_layout.addWidget(self.show_label)
        label_layout.addWidget(self.asset_label)
        label_layout.addWidget(self.info_button)

        cbox_layout = QHBoxLayout()

        cbox_layout.addWidget(self.show_cbox)
        cbox_layout.addWidget(self.asset_cbox)

        browse_button_layout = QHBoxLayout()
        browse_button_layout.addWidget(self.browse_components_button)

        layout.addLayout(label_layout)
        layout.addLayout(cbox_layout)
        layout.addLayout(browse_button_layout)

    def add_connections(self):
        """
        Add signal-slot connections for the widget.
        """
        self.show_cbox.currentIndexChanged.connect(self.on_show_changed)
        self.asset_cbox.currentIndexChanged.connect(self.on_asset_changed)

        self.browse_components_button.clicked.connect(self.browse_components)

    def on_show_changed(self):
        """
        Update the data paths when the show combobox selection changes.
        """
        self.c_data.path = os.path.join(self.c_show_model.path, self.show_cbox.currentText())
        self.c_data.component_path = os.path.join(self.c_data.path, self.asset_cbox.currentText())

    def on_asset_changed(self):
        """
        Update the data paths when the asset combobox selection changes.
        """
        self.c_data.component_path = os.path.join(self.c_data.path, self.asset_cbox.currentText())

    def browse_components(self):
        """
        Browse all components for the selected project path.
        """
        self.c_component.project_path = self.c_data.component_path
        self.c_component.browse_all_components()
