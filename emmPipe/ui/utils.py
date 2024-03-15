import os

from PySide2 import QtCore
from PySide2 import QtWidgets
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
    

class DockableUI(QtWidgets.QWidget):

    WINDOW_TITLE = 'DockableUI'

    ui_instance = None

    @classmethod
    def display(cls):
        if cls.ui_instance:
             cls.ui_instance.restore_workspace_control()
        else:
            cls.ui_instance = cls()
        
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

        self.setObjectName(self.__class__.__name__)

        self.create_workspace_control()

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



