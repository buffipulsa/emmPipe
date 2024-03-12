import os

from PySide2.QtCore import QObject

from emmPipe.rig.component.component import Component


class UIController(QObject):
    
        def __init__(self):
            super().__init__()

            self._show = None
            self._asset = None

            self.build_script_path = 'build/build.py'

        @property
        def show(self):
            return self._show
        
        @show.setter
        def show(self, value):
            self._show = value
        
        @property
        def asset(self):
            return self._asset
        
        @asset.setter
        def asset(self, value):
            self._asset = value

        @property
        def projects_path(self):
            return os.environ['EMMPIPE_PROJECTS_PATH']
    
        @property
        def component_path(self):
            return os.path.join(self.projects_path, self.show, self.asset)

        def print_build_script_path(self):
            print(os.path.join(self.projects_path, self.show, self.asset, self.build_script_path)) 