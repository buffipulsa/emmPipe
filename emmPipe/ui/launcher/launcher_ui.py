import os
import tkinter as tk
from tkinter import ttk


class LauncherUI(tk.Tk):

    CODE_PATH = r"D:\Rigs\emmPipe"
    MAYA_PATH = r"C:\Program Files\Autodesk\Maya{}\bin\maya.exe"
    ICONS_PATH = os.path.join(CODE_PATH, "icons")

    def __init__(self):
        super(LauncherUI, self).__init__()
        self.title("emmPipe Launcher")
        self.geometry("300x200")
        self.create_widgets()

    def create_widgets(self):
        """
        Create the widgets for the launcher UI.

        This method creates the necessary widgets for the launcher UI.
        """
        maya_button = MayaIconButton(self, 
                                    icon_path=f'{__class__.ICONS_PATH}/mayaico.png',
                                    command=self.run_maya)

        maya_version_listbox = MayaVersionComboBox(self)

    def run_maya(self):
        """
        Opens and runs Maya using the specified Maya version.
        """
        os.startfile(__class__.MAYA_PATH.format(self.get_maya_version()))
        
        return 
    
    def get_maya_version(self):
        """
        Get the version of Maya to run.

        Returns:
            str: The version of Maya to run.
        """
        return self.versionListbox.get()
    
    def get_icon(self, path):
        """
        Get the icon from the specified path.

        Args:
            path (str): The path to the icon.

        Returns:
            PhotoImage: The icon.
        """
        return tk.PhotoImage(file=path)
    

class MayaVersionComboBox(ttk.Combobox):
    """
    A custom Combobox widget for Maya versions.

    Args:
        master (tkinter.Tk or tkinter.Toplevel): The parent widget.

    Keyword Args:
        Any additional keyword arguments accepted by tkinter.Button.

    Example:
        combobox = MayaVersionComboBox(root)
    """
    def __init__(self, master, **kwargs):
        super(MayaVersionComboBox, self).__init__(master, **kwargs)
        self.pack(pady=5)
        self["values"] = ["2024", "2023", "2020"]
        self.set("2024")

class MayaIconButton(tk.Button):
    """
    A custom button widget for Maya with an icon.

    Args:
        master (tkinter.Tk or tkinter.Toplevel): The parent widget.
        icon_path (str): The path to the icon image file.

    Keyword Args:
        Any additional keyword arguments accepted by tkinter.Button.

    Attributes:
        icon (tkinter.PhotoImage): The icon image.

    Example:
        button = MayaIconButton(root, "path/to/icon.png")
    """
    def __init__(self, master, icon_path, **kwargs):
        super(MayaIconButton, self).__init__(master, **kwargs)
        self.icon = tk.PhotoImage(file=icon_path)
        self.config(image=self.icon)
        self.pack(pady=5)
    

if __name__ == "__main__":

    launcher_ui = LauncherUI()
    launcher_ui.mainloop()
