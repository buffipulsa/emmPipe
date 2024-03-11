import os

from PySide2.QtCore import QObject


class UIController(QObject):
    
        def __init__(self):
            super().__init__()

            self.show = None
            self.asset = None
            self.build_script_path = 'python/rigBuild/build.py'

        @property
        def projects_path(self):
            return os.environ['EMMPIPE_PROJECTS_PATH']
        
        def print_asset_path(self):
            print(self.asset_path)

        def print_build_script_path(self):
            print(os.path.join(self.projects_path, self.show, self.asset, self.build_script_path))

        def update_show_path(self, show):
            self.show_path = show
            self.update_asset_path()

        def update_asset_path(self):
            self.asset_path =  os.path.join(self.projects_path, self.show_path, self.asset_path)

        def update_show(self, show):
            self.show = show

        def update_asset(self, asset):
            self.asset = asset