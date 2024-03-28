import os


class CodePaths():

    BASEPATH = r'D:\Rigs'
    PROJECTS_PATH = os.path.join(BASEPATH, 'Projects')
    REPO_PATH = os.path.join(BASEPATH, 'emmPipe')

    @classmethod
    def get_basepath(cls):
        return cls.BASEPATH
    
    @classmethod
    def get_projects_path(cls):
        return cls.PROJECTS_PATH
    
    @classmethod
    def get_repo_path(cls):
        return cls.REPO_PATH

class MayaPaths():

    MAYA_PATH = r"C:\Program Files\Autodesk\Maya{}\bin\maya.exe"

    MAYA_SCRIPT_PATH = os.path.join(CodePaths.get_repo_path(), 'emmPipe', 'emmPipe')
    PLUGIN_PATH = os.path.join(CodePaths.get_repo_path(), "plug-ins")
    ICONS_PATH = os.path.join(CodePaths.get_repo_path(), "icons")
    PROD_SHELF_PATH = os.path.join(CodePaths.get_repo_path(), "shelves", 'prod')
    DEV_SHELF_PATH = os.path.join(CodePaths.get_repo_path(), "shelves", 'dev')

    @classmethod
    def get_maya_path(cls, version):
        return cls.MAYA_PATH.format(version)
    
    @classmethod
    def get_maya_script_path(cls):
        return cls.MAYA_SCRIPT_PATH

    @classmethod
    def get_plugin_path(cls):
        return cls.PLUGIN_PATH
    
    @classmethod
    def get_icons_path(cls):
        return cls.ICONS_PATH
    
    @classmethod
    def get_prod_shelf_path(cls):
        return cls.PROD_SHELF_PATH
    
    @classmethod
    def get_dev_shelf_path(cls):
        return cls.DEV_SHELF_PATH


class UnrealEnginePaths():

    pass

