import os

from PySide2 import QtWidgets
from PySide2.QtWidgets import QVBoxLayout

import maya.cmds as cmds

from emmPipe.ui.osseous.osseousUI import OsseousUI

class RigWidget(QtWidgets.QWidget):
    
        def __init__(self, c_data, c_component, parent=None):
            super().__init__(parent)
    
            self.c_data = c_data
            self.c_component = c_component

            self.add_widgets()
            self.add_layouts()

            #self.update_build_script_path()
        
        def add_widgets(self):
            
            self.osseous_button = QtWidgets.QPushButton('Osseous')
            self.button = QtWidgets.QPushButton('Build')

        def add_layouts(self):
            main_layout = QVBoxLayout(self)
            
            main_layout.addWidget(self.osseous_button)
            main_layout.addWidget(self.button)
        
        def add_connections(self):
            self.button.clicked.connect(self.c_data.print_build_script_path)

            self.osseous_button.clicked.connect(self.show_osseous_ui)

        def update_build_script_path(self):
            self.c_data.build_scripts_path = os.path.join(self.c_data.asset, 'python', 'rigBuild', 'build.py')

        def show_osseous_ui(self):

            if os.getenv('EMMPIPE_MODE') == 'Development':
                if cmds.workspaceControl(OsseousUI.get_workspace_control_name(), q=True, exists=True):
                    cmds.deleteUI(OsseousUI.get_workspace_control_name())
                
                print(f'{OsseousUI.get_workspace_control_name()} Deleted')
            
            OsseousUI.display()