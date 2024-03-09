import os

from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2.QtWidgets import QVBoxLayout, QHBoxLayout, QStackedWidget
from PySide2.QtWidgets import QTabWidget, QTabBar


from emmPipe.ui.utils import DockableUI
from emmPipe.ui.utils import set_stylesheet

class MainUI(DockableUI):

    WINDOW_TITLE = 'emmPipe'

    WINDOW_WIDTH = 300
    WINDOW_HEIGHT = 600

    def __init__(self):
        super().__init__()

        set_stylesheet(self, 'VisualScript')

    def add_widgets(self):

        self.tab_bar = CustomTabBar(self)
        self.tab_bar.setFixedWidth(self.WINDOW_WIDTH)

        asset_widget = AssetWidget(self)
        model_widget = ModelWidget(self)
        rig_widget = RigWidget(self)

        self.tab_bar.add_tab(asset_widget, 'Asset')
        self.tab_bar.add_tab(model_widget, 'Model')
        self.tab_bar.add_tab(rig_widget, 'Rig')

    def add_layouts(self):

        layout = QHBoxLayout(self)
        layout.addStretch()
        layout.addWidget(self.tab_bar)


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
        #layout.setContentsMargins(100, 100, 100, 100)
        layout.addStretch()

        layout.addWidget(self.tab_bar)
        layout.addWidget(self.stacked_widget)

    def add_connections(self):
         self.tab_bar.currentChanged.connect(self.stacked_widget.setCurrentIndex)

    def add_tab(self, widget, label):
        self.tab_bar.addTab(label)

        self.stacked_widget.addWidget(widget)


class AssetWidget(QtWidgets.QWidget):
    
        def __init__(self, parent=None):
            super().__init__(parent)
    
            self.add_widgets()
            self.add_layouts()
        
        def add_widgets(self):
            
            self.button = QtWidgets.QPushButton('Asset')

        def add_layouts(self):
            main_layout = QVBoxLayout(self)
            
            main_layout.addWidget(self.button)

class ModelWidget(QtWidgets.QWidget):
    
        def __init__(self, parent=None):
            super().__init__(parent)
    
            self.add_widgets()
            self.add_layouts()
        
        def add_widgets(self):
            
            self.button = QtWidgets.QPushButton('Model')

        def add_layouts(self):
            main_layout = QVBoxLayout(self)
            
            main_layout.addWidget(self.button)

class RigWidget(QtWidgets.QWidget):
    
        def __init__(self, parent=None):
            super().__init__(parent)
    
            self.add_widgets()
            self.add_layouts()
        
        def add_widgets(self):
            
            self.button = QtWidgets.QPushButton('Rig')

        def add_layouts(self):
            main_layout = QVBoxLayout(self)
            
            main_layout.addWidget(self.button)