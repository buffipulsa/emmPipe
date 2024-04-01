import os

from PySide2.QtCore import QStringListModel


class UIPathModel(QStringListModel):
    """
    Model class for representing a list of paths in a user interface.
    """
    def __init__(self, path=None, parent=None):
        super().__init__(parent)

        self._path = path
        self._component_path = None

        if self._path:
            self.path = self._path

    @property
    def path(self):
        """
        Get the current path.
        """
        return self._path

    @path.setter
    def path(self, value):
        """
        Set the current path and update the string list with the contents of the new path.
        """
        self._path = value
        self.setStringList(os.listdir(self._path))

    @property
    def component_path(self):
        """
        Get the current component path.
        """
        return self._component_path
    
    @component_path.setter
    def component_path(self, value):
        """
        Set the current component path.
        """
        self._component_path = value



