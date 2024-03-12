import os

from PySide2.QtCore import QObject

from emmPipe.rig.component.component import Component


class UIController(QObject):
    
        def __init__(self):
            super().__init__()

            self.show = None
            self.asset = None

            self.build_script_path = 'build/build.py'

        @property
        def projects_path(self):
            return os.environ['EMMPIPE_PROJECTS_PATH']
    
        @property
        def component_path(self):
            print(self.show)
            print(self.asset)
            print(os.path.join(self.projects_path, self.show, self.asset))
            return os.path.join(self.projects_path, self.show, self.asset)

        def print_build_script_path(self):
            print(os.path.join(self.projects_path, self.show, self.asset, self.build_script_path))

        def update_show(self, show):
            self.show = show

        def update_asset(self, asset):
            self.asset = asset