import os

from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2.QtWidgets import QVBoxLayout, QHBoxLayout, QStackedWidget
from PySide2.QtWidgets import QTabWidget, QTabBar


from ui.ui_utils import DockableUI, set_stylesheet
from ui.ui_path_model import UIPathModel

from .widgets.asset_widget import AssetWidget
from .widgets.model_widget import ModelWidget
from .widgets.rig_widget import RigWidget

from rig.component import component


class MainUI(DockableUI):
    """
    The main user interface class for the emmPipe application.
    """

    WINDOW_TITLE = 'emmPipe'

    WINDOW_WIDTH = 350
    WINDOW_HEIGHT = 1000

    def __init__(self):
        super().__init__()

        self.c_data = UIPathModel()
        self.c_component = component.Component(self.c_data.component_path)

        self.add_widgets()
        self.add_layouts()
        self.add_connections()

        set_stylesheet(self, 'VisualScript')

    def add_widgets(self):
        """
        Adds the widgets to the main UI.
        """

        self.tab_bar = CustomTabBar(self)
        self.tab_bar.setFixedWidth(self.WINDOW_WIDTH)

        self.asset_widget = AssetWidget(self.c_data, self.c_component, self)
        self.model_widget = ModelWidget(self.c_data, self.c_component, self)
        self.rig_widget = RigWidget(self.c_data, self.c_component, self)

        self.tab_bar.add_tab(self.asset_widget, 'Asset')
        self.tab_bar.add_tab(self.model_widget, 'Model')
        self.tab_bar.add_tab(self.rig_widget, 'Rig')

    def add_layouts(self):
        """
        Adds the layouts to the main UI.
        """

        layout = QVBoxLayout(self)

        layout.addWidget(self.tab_bar, alignment=QtCore.Qt.AlignTop)

    def add_connections(self):
        """
        Adds the connections between widgets and signals.
        """

        self.asset_widget.add_connections()
        self.model_widget.add_connections()
        self.rig_widget.add_connections()

    def center_window(self, window):
        """
        Centers the given window on the screen.
        """

        frame_geometry = window.frameGeometry()
        center_point = QtCore.QCoreApplication.instance().desktop().availableGeometry().center()
        frame_geometry.moveCenter(center_point)
        window.move(frame_geometry.topLeft())
    

class CustomTabBar(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.parent = parent

        self.add_widgets()
        self.add_layouts()
        self.add_connections()

    def add_widgets(self):
    
        self.tab_bar = QTabBar()
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setFixedHeight(self.parent.height())
    
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


