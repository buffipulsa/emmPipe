import os

from PySide2.QtCore import QStringListModel


class UIPathModel(QStringListModel):

    def __init__(self, path=None, parent=None):
        super().__init__(parent)

        self._path = path
        self._component_path = None

        if self._path:
            self.path = self._path

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, value):
        self._path = value
        self.setStringList(os.listdir(self._path))

    @property
    def component_path(self):
        return self._component_path
    
    @component_path.setter
    def component_path(self, value):
        self._component_path = value

