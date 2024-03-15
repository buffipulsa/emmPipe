import os

from PySide2.QtWidgets import QFileSystemModel
from PySide2.QtCore import QObject, QStringListModel

from emmPipe.rig.component.component import Component


class UIPathModel(QStringListModel):

    def __init__(self, parent=None):
        super().__init__(parent)

        self._projects_path = os.environ['EMMPIPE_PROJECTS_PATH']

        self.setStringList(self.get_projects())

        self.assets = self.get_assets()

    def get_projects(self):
            """
            Get the projects from the specified path.

            Returns:
                list: The projects.
            """
            return os.listdir(self._projects_path)
        
    def get_assets(self):
        """
        Get the assets from the specified path.

        Returns:
            list: The assets.
        """
        return os.listdir(os.path.join(self._projects_path, self.data(self.index(0, 0))))
    
    @property
    def root_index(self):
        return self._root_index

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