import os

from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
from shiboken2 import wrapInstance, getCppPointer

import maya.OpenMayaUI as omui
import maya.cmds as cmds


def set_stylesheet(widget, stylesheet=None):
    """
    Set the stylesheet for a given widget.

    Args:
        widget (QWidget): The widget to set the stylesheet for.
        stylesheet (str): The name of the stylesheet file to use. If not provided, no stylesheet will be set.

    Returns:
        None
    """
    STYLESHEET_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), f'data\stylesheets\{stylesheet}.qss'))

    if stylesheet and os.path.exists(STYLESHEET_PATH):
        with open(STYLESHEET_PATH, 'r') as f:
            widget.setStyleSheet(f.read())
    else:
        cmds.warning(f"Stylesheet not found: {stylesheet}")

def maya_main_window():
    """
    Returns the main Maya window as a QtWidgets.QWidget instance.
    
    Returns:
        QtWidgets.QWidget: The main Maya window.
    """
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)


class WorkspaceControl(object):

    def __init__(self, name):
        self.name = name
        self.widget = None

    def create(self, label, widget, ui_script=None):
        cmds.workspaceControl(self.name, label=label)

        if ui_script:
            cmds.workspaceControl(self.name, edit=True, uiScript=ui_script)
        
        self.add_widget_to_layout(widget)
        self.restore_ui()

    def restore_widget(self, widget):
        self.add_widget_to_layout(widget)

    def add_widget_to_layout(self, widget):
        if widget:
            self.widget = widget
            self.widget.setAttribute(QtCore.Qt.WA_DontCreateNativeAncestors)

            workspace_control_ptr = int(omui.MQtUtil.findControl(self.name))
            widget_ptr = int(getCppPointer(self.widget)[0])

            omui.MQtUtil.addWidgetToMayaLayout(widget_ptr, workspace_control_ptr)

    def exists(self):
        return cmds.workspaceControl(self.name, query=True, exists=True)
    
    def restore_ui(self):
        cmds.workspaceControl(self.name, edit=True, restore=True)
    
    def close(self):
        cmds.workspaceControl(self.name, edit=True, close=True)
    
    def hide(self):
        cmds.workspaceControl(self.name, edit=True, visible=False)

    def fixed_size(self, width, height):
        cmds.workspaceControl(self.name, edit=True, width=width, height=height, widthProperty='fixed', heightProperty='fixed')

class DockableUI(QtWidgets.QWidget):

    WINDOW_TITLE = 'DockableUI'

    WINDOW_WIDTH = 350
    WINDOW_HEIGHT = 500

    ui_instance = None

    @classmethod
    def display(cls):
        if cls.ui_instance:
             cls.ui_instance.restore_workspace_control()
        else:
            cls.ui_instance = cls()
    
    @classmethod
    def close(cls):
        if cls.ui_instance:
            cls.ui_instance.workspace_control.close()
            cls.ui_instance = None
    
    @classmethod
    def hide(cls):
        if cls.ui_instance:
            cls.ui_instance.workspace_control.hide()
        
    @classmethod
    def get_workspace_control_name(cls):
         return f'{cls.__name__}WorkspaceControl'
    
    @classmethod
    def get_ui_script(cls):
        module_name = cls.__module__
        if module_name == "__main__":
            module_name = cls.module_name_override

        ui_script = "from {0} import {1}\n{1}.display()".format(module_name, cls.__name__)

        return ui_script

    def __init__(self):
        super().__init__()

        self.setFixedHeight(self.WINDOW_HEIGHT)
        self.setFixedWidth(self.WINDOW_WIDTH)

        self.setObjectName(self.__class__.__name__)

        self.create_workspace_control()

        self.workspace_control.fixed_size(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)

    def add_widgets(self):
        raise NotImplementedError('Subclasses must implement the add_widgets method.')

    def add_layouts(self):
        raise NotImplementedError('Subclasses must implement the add_layout method.')

    def add_connections(self):
        raise NotImplementedError('Subclasses must implement the add_connections method.')
    
    def create_workspace_control(self):
        self.workspace_control = WorkspaceControl(self.get_workspace_control_name())
        if self.workspace_control.exists():
            self.workspace_control.restore_widget(self)
        else:
            self.workspace_control.create(self.WINDOW_TITLE, self, 
                                          ui_script=self.get_ui_script())
    
    def restore_workspace_control(self):
        self.workspace_control.restore_ui()


class InfoButtonWidget(QtWidgets.QPushButton):

    def __init__(self, parent=None, message=None):
        super().__init__(parent)

        self.message = message

        self.setText('?')
        self.setFixedWidth(25)
        
        self.add_connections()

    def add_connections(self):
        self.clicked.connect(self.show_info)

    def show_info(self):
        info = self.get_info()

        message_box = QtWidgets.QMessageBox()
        message_box.information(self, 'Guide', info)

    def get_info(self):
        if self.message:
            return self.message
        else:
            raise ValueError('Please provide a message.')
        

class CollapsibleHeader(QtWidgets.QWidget):

    COLLAPSED_PIXMAD = QtGui.QPixmap(':teRightArrow.png')
    EXPANDED_PIXMAD = QtGui.QPixmap(':teDownArrow.png')

    LABEL_COLOR = '#565656'

    clicked = QtCore.Signal()

    def __init__(self, title, parent=None):
        super().__init__(parent)

        self.title = title

        self.add_widgets()
        self.add_layouts()

        self.set_title(self.title)
        self.set_expanded(False)

    def add_widgets(self):

        self.icon_label = QtWidgets.QLabel()
        self.icon_label.setContentsMargins(0, 0, 0, 0)
        self.icon_label.setAlignment(QtCore.Qt.AlignCenter)
        self.icon_label.setFixedWidth(self.COLLAPSED_PIXMAD.width() + 20)
        self.icon_label.setFixedHeight(self.COLLAPSED_PIXMAD.height() + 10)
        self.icon_label.setStyleSheet(f'background-color: {self.LABEL_COLOR};')

        self.title_label = QtWidgets.QLabel()
        self.title_label.setContentsMargins(0, 0, 0, 0)
        self.title_label.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
        self.title_label.setFixedHeight(self.COLLAPSED_PIXMAD.height() + 10)
        self.title_label.setStyleSheet(f'background-color: {self.LABEL_COLOR};')

    
    def add_layouts(self):
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self.icon_label)
        layout.addWidget(self.title_label)

    def set_title(self, title):
        self.title_label.setText(f'<b>{title}</b>')

    def is_expanded(self):
        return self._expanded
    
    def set_expanded(self, state):
        self._expanded = state

        if self._expanded:
            self.icon_label.setPixmap(self.EXPANDED_PIXMAD)
        else:
            self.icon_label.setPixmap(self.COLLAPSED_PIXMAD)
    
    def mouseReleaseEvent(self, event):
        self.clicked.emit()


class CollapsibleWidget(QtWidgets.QWidget):

    def __init__(self, title, parent=None):
        super().__init__(parent)

        self.title = title

        self.add_widgets()
        self.add_layouts()
        self.add_connections()

        self.toggle_expanded(False)

    def add_widgets(self):

        self.header_widget = CollapsibleHeader(self.title)

        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.scroll_area.setWidgetResizable(True)
        #self.scroll_area.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
    
    def add_layouts(self):
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.layout.addWidget(self.header_widget)
        self.layout.addWidget(self.scroll_area)

        self.setLayout(self.layout)

    def add_connections(self):
        self.header_widget.clicked.connect(self.on_header_clicked)

    def toggle_expanded(self, state):
        self.header_widget.set_expanded(state)
        self.scroll_area.setVisible(state)

    def on_header_clicked(self):
        self.toggle_expanded(not self.header_widget.is_expanded())
