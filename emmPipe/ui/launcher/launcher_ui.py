
import os
import tkinter as tk
import ttkbootstrap as ttk


class LauncherUI(ttk.Window):
    """
    The main class for the emmPipe Launcher UI.

    This class represents the application window and contains methods for setting up the UI,
    handling user interactions, and launching Maya.
    """

    MAYA_PATH = r"C:\Program Files\Autodesk\Maya{}\bin\maya.exe"

    BASEPATH = r'D:\Rigs'
    PROJECTS_PATH = os.path.join(BASEPATH, 'Projects')
    REPO_PATH = os.path.join(BASEPATH, 'emmPipe')
    MAYA_SCRIPT_PATH = os.path.join(BASEPATH, 'emmPipe', 'emmPipe')
    
    PLUGIN_PATH = os.path.join(REPO_PATH, "plug-ins")
    ICONS_PATH = os.path.join(REPO_PATH, "icons")
    PROD_SHELF_PATH = os.path.join(REPO_PATH, "shelves", 'prod')
    DEV_SHELF_PATH = os.path.join(REPO_PATH, "shelves", 'dev')

    APP_ICON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'launcher_ui.png')

    WINDOW_WIDTH = 300
    WINDOW_HEIGHT = 300

    def __init__(self):
        super(LauncherUI, self).__init__()

        self.title("emmPipe Launcher")

        ttk.Style().theme_use('darkly')
        
        self.geometry(f"{__class__.WINDOW_WIDTH}x{__class__.WINDOW_HEIGHT}")
        self.center_window(__class__.WINDOW_WIDTH, __class__.WINDOW_HEIGHT)

        self.resizable(False, False)

        self.set_icon()

        self.create_widgets()

        return

    def set_paths(self):
        """
        Sets the necessary environment variables for the launcher.

        This method sets the PYTHONPATH, MAYA_PLUG_IN_PATH, MAYA_SHELF_PATH, and XBMLANGPATH
        environment variables to the appropriate paths for emmPipe.
        """
        os.environ["PYTHONPATH"] = __class__.REPO_PATH
        os.environ["MAYA_SCRIPT_PATH"] = __class__.MAYA_SCRIPT_PATH
        os.environ["MAYA_PLUG_IN_PATH"] = __class__.PLUGIN_PATH
        os.environ["MAYA_SHELF_PATH"] = __class__.PROD_SHELF_PATH
        os.environ["XBMLANGPATH"] = __class__.ICONS_PATH
        os.environ["EMMPIPE_PROJECTS_PATH"] = __class__.PROJECTS_PATH
        os.environ["EMMPIPE_MODE"] = self.prod_or_dev_cbox.get()

        self.set_mode_to_dev_or_prod(os.environ["EMMPIPE_MODE"])

        return
    
    def set_icon(self):
        """
        Sets the icon for the application window.

        This method loads an image file specified by the `APP_ICON_PATH` class attribute
        and sets it as the icon for the application window.
        """
        img = tk.PhotoImage(file=__class__.APP_ICON_PATH)
        self.tk.call('wm', 'iconphoto', self._w, img)

        return

    def center_window(self, width, height):
        """
        Center the window on the screen.

        Args:
            width (int): The width of the window.
            height (int): The height of the window.
        """
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        x = (screen_width / 2) - (width / 2)
        y = (screen_height / 2) - (height / 2)

        self.geometry(f"{width}x{height}+{int(x)}+{int(y)}")

        return

    def create_widgets(self):
        """
        Create the widgets for the launcher UI.

        This method creates the necessary widgets for the launcher UI, including the menu bar,
        Maya icon button, and Maya version combo box.
        """

        self.menu_bar = MenuBar(self)
        self.config(menu=self.menu_bar)

        self.prod_or_dev_cbox = CustomComboBox(self, values=['Production', 'Development'])

        self.maya_button = MayaIconButton(self, command=self.run_maya)

        self.maya_version_cbox = CustomComboBox(self, values=['2024', '2023', '2020'])

        return

    def run_maya(self):
        """
        Opens and runs Maya using the specified Maya version.
        """
        self.set_paths()

        os.startfile(__class__.MAYA_PATH.format(self.get_maya_version()))
        
        return 
    
    def get_maya_version(self):
        """
        Get the version of Maya to run.

        Returns:
            str: The version of Maya to run.
        """
        return self.maya_version_cbox.get()
    
    def get_icon(self, path):
        """
        Get the icon from the specified path.

        Args:
            path (str): The path to the icon.

        Returns:
            PhotoImage: The icon.
        """
        return tk.PhotoImage(file=path)

    def set_mode_to_dev_or_prod(self, mode):
        """
        Set the environment variables for development mode.
        """
        if mode == 'Development':
            os.environ["MAYA_SHELF_PATH"] = __class__.DEV_SHELF_PATH
        
            os.environ['MAYA_NO_CONSOLE_WINDOW'] = '0'
            os.environ['MAYA_DISABLE_CIP'] = '1'
            os.environ['MAYA_DISABLE_CLIC_IPM'] = '1'
            os.environ['MAYA_DISABLE_CER'] = '1'


        if mode == 'Production':
            os.environ["MAYA_SHELF_PATH"] = __class__.PROD_SHELF_PATH

            os.environ['MAYA_NO_CONSOLE_WINDOW'] = '1'

        return

class MenuBar(ttk.Menu):
    """
    A custom MenuBar widget for the launcher UI.

    Args:
        master (tkinter.Tk or tkinter.Toplevel): The parent widget.
    """
    def __init__(self, master):
        super(MenuBar, self).__init__(master)

        file_menu = tk.Menu(self, tearoff=False)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=master.quit)

        self.add_cascade(label="File", menu=file_menu)

class CustomComboBox(ttk.Combobox):
    """
    A custom Combobox widget for Maya versions.

    Args:
        master (tkinter.Tk or tkinter.Toplevel): The parent widget.

    Keyword Args:
        Any additional keyword arguments accepted by tkinter.Button.

    Example:
        combobox = MayaVersionComboBox(root)
    """
    def __init__(self, master, values=None, **kwargs):
        super(CustomComboBox, self).__init__(master, **kwargs)
        self["values"] = values
        self.set(values[0])
        self.pack(pady=20)

        self.bind("<FocusIn>", self.on_combobox_click)
        self.bind("<FocusOut>", self.on_combobox_leave)

    def on_combobox_click(self, event):
        """
        Event handler for the combobox click event.

        Args:
            event (tkinter.Event): The event object.
        """
        self.state(['readonly']) 
    
    def on_combobox_leave(self, event):
        """
        Event handler for the combobox leave event.

        Args:
            event (tkinter.Event): The event object.
        """
        self.state(['!readonly'])

class MayaIconButton(ttk.Button):
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
    def __init__(self, master, **kwargs):
        super(MayaIconButton, self).__init__(master, **kwargs)
        self.icon = tk.PhotoImage(file=f'{master.ICONS_PATH}/mayaico.png')
        self.config(image=self.icon)
        self.pack()
    

if __name__ == "__main__":

    launcher_ui = LauncherUI()
    launcher_ui.mainloop()
