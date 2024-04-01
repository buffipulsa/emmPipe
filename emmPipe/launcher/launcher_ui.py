
import os
import tkinter as tk
import ttkbootstrap as ttk
from PIL import Image, ImageTk


from path_utils import CodePaths, MayaPaths, UnrealEnginePaths

class LauncherUI(ttk.Window):
    """
    The main class for the emmPipe Launcher UI.

    This class represents the application window and contains methods for setting up the UI,
    handling user interactions, and launching Maya.
    """

    FILE_DIR = os.path.dirname(os.path.abspath(__file__))

    WINDOW_WIDTH = 350
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
        self.create_layout()

        self.set_emmpipe_paths()

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
        self.maya_version_cbox = CustomComboBox(self, values=MayaPaths.get_version())

        self.unreal_engine_button = UnrealEngineIconButton(self, command=self.run_unreal_engine)
        self.unreal_engine_version_cbox = CustomComboBox(self, values=UnrealEnginePaths.get_version())

        return
    
    def create_layout(self):

        self.prod_or_dev_cbox.grid(row=0, column=0, padx=10, pady=20)
        
        self.maya_button.grid(row=1, column=0, padx=10, pady=10)
        self.maya_version_cbox.grid(row=2, column=0, padx=10, pady=10)
        
        self.unreal_engine_button.grid(row=1, column=1, padx=10, pady=10)
        self.unreal_engine_version_cbox.grid(row=2, column=1, padx=10, pady=10)

    def set_emmpipe_paths(self):

        os.environ["EMMPIPE_PROJECTS_PATH"] = CodePaths.get_projects_path()
        os.environ["EMMPIPE_MODE"] = self.prod_or_dev_cbox.get()

    def set_maya_paths(self):
        """
        Sets the necessary environment variables for the launcher.

        This method sets the PYTHONPATH, MAYA_PLUG_IN_PATH, MAYA_SHELF_PATH, and XBMLANGPATH
        environment variables to the appropriate paths for emmPipe.
        """

        os.environ['PYTHONPATH'] = MayaPaths.get_scripts_path()
        os.environ['MAYA_SCRIPT_PATH'] = MayaPaths.get_scripts_path()
        os.environ["MAYA_PLUG_IN_PATH"] = MayaPaths.get_plugin_path()
        # os.environ["MAYA_SHELF_PATH"] = MayaPaths.get_prod_shelf_path()
        os.environ["XBMLANGPATH"] = MayaPaths.get_icons_path()

        self.set_mode_to_dev_or_prod(self.prod_or_dev_cbox.get())

        return
    
    def set_unreal_engine_paths(self):
        
        os.environ['UE_PYTHONPATH'] = UnrealEnginePaths.get_scripts_path()

    def set_mode_to_dev_or_prod(self, mode):
        """
        Set the environment variables for development mode.
        """
        if mode == 'Development':
            os.environ["MAYA_SHELF_PATH"] = MayaPaths.get_dev_shelf_path()
        
            os.environ['MAYA_NO_CONSOLE_WINDOW'] = '0'
            os.environ['MAYA_DISABLE_CIP'] = '1'
            os.environ['MAYA_DISABLE_CLIC_IPM'] = '1'
            os.environ['MAYA_DISABLE_CER'] = '1'


        if mode == 'Production':
            os.environ["MAYA_SHELF_PATH"] = MayaPaths.get_prod_shelf_path()

            os.environ['MAYA_NO_CONSOLE_WINDOW'] = '1'

        return


    def set_icon(self):
        """
        Sets the icon for the application window.

        This method loads an image file specified by the `APP_ICON_PATH` class attribute
        and sets it as the icon for the application window.
        """
        img = tk.PhotoImage(file=os.path.join(self.FILE_DIR, 'icons', 'launcher_ui.png'))
        self.tk.call('wm', 'iconphoto', self._w, img)

        return

    def run_maya(self):
        """
        Opens and runs Maya using the specified Maya version.
        """
        self.set_maya_paths()

        os.startfile(MayaPaths.get_exe_path(self.get_maya_version()))
        
        return 
    
    def run_unreal_engine(self):
        """
        Opens and runs Unreal Engine using the specified version.
        """

        self.set_unreal_engine_paths()

        os.startfile(UnrealEnginePaths.get_exe_path(self.unreal_engine_version_cbox.get()))

        return
    
    def get_maya_version(self):
        """
        Get the version of Maya to run.

        Returns:
            str: The version of Maya to run.
        """
        return self.maya_version_cbox.get()
    
    def get_unreal_engine_version(self):
        """
        Get the version of Unreal Engine to run.

        Returns:
            str: The version of Unreal Engine to run.
        """
        return self.unreal_engine_version_cbox.get()
    
    def get_icon(self, path):
        """
        Get the icon from the specified path.

        Args:
            path (str): The path to the icon.

        Returns:
            PhotoImage: The icon.
        """
        return tk.PhotoImage(file=path)


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
    A custom button widget that displays an icon for Maya.
    """

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.icon = tk.PhotoImage(file=f'{master.FILE_DIR}/icons/mayaico.png')
        self.config(image=self.icon, width=self.icon.width())
        

class UnrealEngineIconButton(ttk.Button):
    """
    A custom button widget that displays an icon for Unreal Engine.
    """

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        original_icon = Image.open(f'{master.FILE_DIR}/icons/ue_logo.png')
        scaled_icon = original_icon.resize((128, 128))

        self.icon = ImageTk.PhotoImage(scaled_icon)
        self.config(image=self.icon)

    

if __name__ == "__main__":

    launcher_ui = LauncherUI()
    launcher_ui.mainloop()
