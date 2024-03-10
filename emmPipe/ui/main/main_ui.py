import os

from PySide2 import QtCore
from PySide2.QtCore import QObject
from PySide2 import QtWidgets
from PySide2.QtWidgets import QVBoxLayout, QHBoxLayout, QStackedWidget
from PySide2.QtWidgets import QTabWidget, QTabBar


from emmPipe.ui.utils import DockableUI
from emmPipe.ui.utils import set_stylesheet

from .widgets.asset_widget import AssetWidget
from .widgets.model_widget import ModelWidget
from .widgets.rig_widget import RigWidget

class TestData(QObject):
    
        def __init__(self):
            super().__init__()

            self.asset_path = None
        
        def print_asset_path(self):
            print(self.asset_path)

        @property
        def projects_path(self):
            return os.environ['EMMPIPE_PROJECTS_PATH']


class MainUI(DockableUI):

    WINDOW_TITLE = 'emmPipe'

    WINDOW_WIDTH = 300
    WINDOW_HEIGHT = 600

    def __init__(self):
        super().__init__()

        self.c_data = TestData()

        self.add_widgets()
        self.add_layouts()
        self.add_connections()

        set_stylesheet(self, 'VisualScript')

    def add_widgets(self):

        self.tab_bar = CustomTabBar(self)
        self.tab_bar.setFixedWidth(self.WINDOW_WIDTH)

        self.asset_widget = AssetWidget(self.c_data, self)
        model_widget = ModelWidget(self.c_data, self)
        self.rig_widget = RigWidget(self.c_data, self)

        self.tab_bar.add_tab(self.asset_widget, 'Asset')
        self.tab_bar.add_tab(model_widget, 'Model')
        self.tab_bar.add_tab(self.rig_widget, 'Rig')

    def add_layouts(self):

        layout = QVBoxLayout(self)
        layout.addStretch()
        layout.addWidget(self.tab_bar)
    
    def add_connections(self):
        self.rig_widget.button.clicked.connect(self.c_data.print_asset_path)

    def center_window(self, window):

        frame_geometry = window.frameGeometry()
        center_point = QtCore.QCoreApplication.instance().desktop().availableGeometry().center()
        frame_geometry.moveCenter(center_point)
        window.move(frame_geometry.topLeft())
    

class CustomTabBar(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.add_widgets()
        self.add_layouts()
        self.add_connections()

    def add_widgets(self):
    
        self.tab_bar = QTabBar()
        self.stacked_widget = QStackedWidget()
    
    def add_layouts(self):
        layout = QVBoxLayout(self)
        layout.addStretch()

        layout.addWidget(self.tab_bar)
        layout.addWidget(self.stacked_widget)

    def add_connections(self):
         self.tab_bar.currentChanged.connect(self.stacked_widget.setCurrentIndex)

    def add_tab(self, widget, label):
        self.tab_bar.addTab(label)

        self.stacked_widget.addWidget(widget)


