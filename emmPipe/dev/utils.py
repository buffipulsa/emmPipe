import sys

# if you have some packages that you often reload, you can put them here
# and they will get reloaded if "packages" attribute is not explicitly stated
DEFAULT_RELOAD_PACKAGES = [] 

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