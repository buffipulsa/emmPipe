import sys

import maya.cmds as cmds
import maya.mel as mel

# if you have some packages that you often reload, you can put them here
# and they will get reloaded if "packages" attribute is not explicitly stated
DEFAULT_RELOAD_PACKAGES = ['rig', 'dev', 'ui', 'controller'] 

def unload_packages(silent=True, packages=None):
    """
    Unloads specified packages from the sys.modules dictionary.
    https://www.aleksandarkocic.com/2020/12/19/live-reload-your-python-code-in-maya/

    Args:
        silent (bool, optional): If True, suppresses the print statements. Defaults to True.
        packages (list, optional): List of package names to unload. If None, uses DEFAULT_RELOAD_PACKAGES. Defaults to None.

    Returns:
        None
    """
    if packages is None:
        packages = DEFAULT_RELOAD_PACKAGES

    # construct reload list
    reloadList = []
    for i in sys.modules.keys():
        for package in packages:
            if i.startswith(package):
                reloadList.append(i)

    # unload everything
    for i in reloadList:
        try:
            if sys.modules[i] is not None:
                del(sys.modules[i])
                if not silent:
                    print("Unloaded: %s" % i)
        except:
            print("Failed to unload: %s" % i)

def create_reload_shelf_button(shelf_name="reloadShelf", button_name="reloadButton", module_to_reload=None):
    """
    Creates a shelf button that reloads the specified packages. 
    https://www.aleksandarkocic.com/2020/12/19/live-reload-your-python-code-in-maya/

    Returns:
        None
    """
    # create shelf
    if not cmds.shelfLayout(shelf_name, exists=True):
        raise ValueError(f'Shelf {shelf_name} does not exist.')

    # create button
    if not cmds.shelfButton(button_name, exists=True):
        if modules_to_reload is None:
            modules_to_reload = DEFAULT_RELOAD_PACKAGES
        else:
            cmds.shelfButton(button_name, parent=shelf_name, label="Reload", command=f'from emmPipe.dev.utils import unload_packages\nunload_packages(silent=False, packages=[{module_to_reload}])\nimport {module_to_reload}', image1="pythonFamily.png", annotation=f"Reloads the {module_to_reload}")

    # set button to run python
    mel.eval('global string $gShelfTopLevel; shelfButton -edit -commandLanguage python $gShelfTopLevel|reloadShelf|reloadButton;')

def convert_list_to_str(list_to_convert):
    """
    Converts a list to a string
    """
    if len(list_to_convert) < 1:
        raise ValueError('List is empty.')
    elif len(list_to_convert) == 1:
        return f"{list_to_convert[0]}"
    else:
        return ','.join([f"{item}" for item in list_to_convert])

def convert_str_to_list(str_to_convert):
    """
    Converts a string to a list.
    """
    if len(str_to_convert) < 1:
        raise ValueError('String is empty.')
    elif not ',' in str_to_convert:
        return [str_to_convert]
    else:
        list_from_convert = str_to_convert.split(',')
        for item in list_from_convert:
            if item == 'None':
                list_from_convert[list_from_convert.index(item)] = None

        return list_from_convert
    
def combine_names(*args):
    """
    Combines the given names into a single string.
    """
    parts = []
    for arg in args:
        if isinstance(arg, str):
            arg = arg.lower()
        if isinstance(arg, int):
            arg = str(arg).zfill(3)
        
        parts.append(arg)
    
    return '_'.join(parts)