import os

from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2.QtWidgets import QVBoxLayout, QHBoxLayout, QStackedWidget
from PySide2.QtWidgets import QTabWidget, QTabBar

from emmPipe.ui.utils import InfoButtonWidget
from emmPipe.rig.component.component import Component

class AssetWidget(QtWidgets.QWidget):

        def __init__(self, c_data, parent=None):
            super().__init__(parent)

            self.c_data = c_data

            self.add_widgets()
            self.add_layouts()

            self.c_data.show = self.show_cbox.currentText()
            self.c_data.asset = self.asset_cbox.currentText()

            self.c_components = Component(self.c_data.component_path)

        def add_widgets(self):
            
            self.info_button = InfoButtonWidget(self, 'Here you can select the show and asset you wish to work on.')

            self.show_label = QtWidgets.QLabel('Show:')
            self.asset_label = QtWidgets.QLabel('Asset:')

            self.show_label.setIndent(5)
            self.asset_label.setIndent(25)

            self.show_cbox = QtWidgets.QComboBox()
            self.asset_cbox = QtWidgets.QComboBox()

            self.show_cbox.addItems(self.get_projects())
            self.asset_cbox.addItems(self.get_assets())

            self.show_cbox.setCurrentText('common')
            self.update_assets_cbox()
            self.asset_cbox.setCurrentText('chrBaseMale')

            self.browse_components_button = QtWidgets.QPushButton('Browse Components')

        def add_layouts(self):

            layout = QVBoxLayout(self,alignment=QtCore.Qt.AlignTop)
            
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
            
            self.show_cbox.currentIndexChanged.connect(self.update_assets_cbox)
            self.show_cbox.currentIndexChanged.connect(lambda _: setattr(self.c_data, 'show', self.show_cbox.currentText()))
            self.asset_cbox.currentIndexChanged.connect(lambda _: setattr(self.c_data, 'asset', self.asset_cbox.currentText()))

            self.browse_components_button.clicked.connect(self.update_selection)
            self.browse_components_button.clicked.connect(lambda _: setattr(self.c_components, 'project_path', self.c_data.component_path))
            self.browse_components_button.clicked.connect(self.c_components.browse_all_components)

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
        
        def update_assets_cbox(self):
            self.asset_cbox.clear()
            self.asset_cbox.addItems(self.get_assets())

        def update_selection(self):
            self.c_data.show = self.show_cbox.currentText()
            self.c_data.asset = self.asset_cbox.currentText()
            print('Show:', self.c_data.show, 'Asset:', self.c_data.asset)
        
        
        