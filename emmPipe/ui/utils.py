
from PySide2 import QtWidgets
from shiboken2 import wrapInstance

import maya.OpenMayaUI as omui


def maya_main_window():
    """
    Returns the main Maya window as a QtWidgets.QWidget instance.
    
    Returns:
        QtWidgets.QWidget: The main Maya window.
    """
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)

