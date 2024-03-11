import os

from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2.QtWidgets import QVBoxLayout, QHBoxLayout, QStackedWidget
from PySide2.QtWidgets import QTabWidget, QTabBar

class AssetWidget(QtWidgets.QWidget):

        def __init__(self, c_data, parent=None):
            super().__init__(parent)

            self.c_data = c_data

            self.add_widgets()
            self.add_layouts()
            self.add_connections()

            self.update_asset_path()
        
        def add_widgets(self):
            
            self.show_label = QtWidgets.QLabel('Show:')
            self.asset_label = QtWidgets.QLabel('Asset:')
            self.asset_label.setIndent(10)

            self.show_cbox = QtWidgets.QComboBox()
            self.asset_cbox = QtWidgets.QComboBox()

            self.show_cbox.addItems(self.get_projects())
            self.asset_cbox.addItems(self.get_assets())

            self.show_cbox.setCurrentText('common')
            self.update_assets()
            self.asset_cbox.setCurrentText('chrBaseMale')

        def add_layouts(self):
            layout = QVBoxLayout(self)
            layout.addSpacing(10)
            
            label_layout = QHBoxLayout()
            label_layout.addSpacing(15)

            label_layout.addWidget(self.show_label)
            label_layout.addWidget(self.asset_label)

            cbox_layout = QHBoxLayout()
            cbox_layout.addSpacing(10)

            cbox_layout.addWidget(self.show_cbox)
            cbox_layout.addWidget(self.asset_cbox)

            layout.addLayout(label_layout)
            layout.addLayout(cbox_layout)
        
        def add_connections(self):
            self.show_cbox.currentIndexChanged.connect(self.update_assets)
            self.asset_cbox.currentIndexChanged.connect(self.update_asset_path)

        def get_projects(self):
            """
            Get the projects from the specified path.

            Returns:
                list: The projects.
            """
            return os.listdir(self.c_data.projects_path)
        
        def get_assets(self):
            """
            Get the assets from the specified path.

            Returns:
                list: The assets.
            """
            return os.listdir(os.path.join(self.c_data.projects_path, self.show_cbox.currentText()))
        
        def update_assets(self):
            self.asset_cbox.clear()
            self.asset_cbox.addItems(self.get_assets())
        
        def update_asset_path(self):
            #print(os.path.join(__class__.PROJECT_PATH, self.show_cbox.currentText(), self.asset_cbox.currentText()))
            self.c_data.asset_path =  os.path.join(self.c_data.projects_path, self.show_cbox.currentText(), self.asset_cbox.currentText())
        