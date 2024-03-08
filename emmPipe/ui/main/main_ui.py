
from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2.QtWidgets import QVBoxLayout
from PySide2.QtWidgets import QTabWidget, QTabBar

from emmPipe.ui.utils import maya_main_window

class MainUI(QtWidgets.QDialog):

    WINDOW_TITLE = 'emmPipe'

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle(MainUI.WINDOW_TITLE)
        self.setWindowFlag(QtCore.Qt.WindowType.Window)
        self.setGeometry(200, 200, 400, 800)
        

        self.add_widgets()
        self.add_layouts()

    def add_widgets(self):

        self.tab_bar = CustomTabBar()

        asset_widget = AssetWidget()
        model_widget = ModelWidget()
        rig_widget = RigWidget()

        self.tab_bar.add_tab(asset_widget, 'Asset')
        self.tab_bar.add_tab(model_widget, 'Model')
        self.tab_bar.add_tab(rig_widget, 'Rig')

    def add_layouts(self):

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0,0,0,0)

        self.layout.addWidget(self.tab_bar)
        
        self.layout.addStretch()


class CustomTabBar(QtWidgets.QWidget):

    def __init__(self, parent=maya_main_window()):
        super().__init__(parent)

        self.add_widgets()
        self.add_layouts()

    def add_widgets(self):
        self.tab_bar = QTabBar()
    
    def add_layouts(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0,0,0,0)

        main_layout.addWidget(self.tab_bar)

    def add_tab(self, widget, label):
        self.tab_bar.addTab(label)


class AssetWidget(QtWidgets.QWidget):
    
        def __init__(self, parent=None):
            super().__init__(parent)
    
            self.add_layouts()
        
        def add_layouts(self):
            main_layout = QVBoxLayout()
            self.setLayout(main_layout)

class ModelWidget(QtWidgets.QWidget):
    
        def __init__(self, parent=None):
            super().__init__(parent)
    
            self.add_layouts()
        
        def add_layouts(self):
            main_layout = QVBoxLayout()
            self.setLayout(main_layout)

class RigWidget(QtWidgets.QWidget):
    
        def __init__(self, parent=None):
            super().__init__(parent)
    
            self.add_layouts()
        
        def add_layouts(self):
            main_layout = QVBoxLayout()
            self.setLayout(main_layout)