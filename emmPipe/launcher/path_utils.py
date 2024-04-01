import os


class CodePaths():

    BASE_PATH = r'D:\Rigs'

    @classmethod
    def get_basepath(cls):
        return cls.BASE_PATH
    
    @classmethod
    def get_projects_path(cls):
        return os.path.join(cls.BASE_PATH, 'Projects')
    
    @classmethod
    def get_repo_path(cls):
        return os.path.join(cls.BASE_PATH, 'emmPipe')

class MayaPaths():

    BASE_PATH = r"C:\Program Files\Autodesk"
    EXE_PATH = r"C:\Program Files\Autodesk\Maya{}\bin\maya.exe"

    @classmethod
    def get_exe_path(cls, version):
        return cls.EXE_PATH.format(version)
    
    @classmethod
    def get_version(cls):

        versions = [version.split('Maya')[-1] for version in os.listdir(cls.BASE_PATH) if version.startswith('Maya20')]
        versions = sorted(versions, reverse=True)

        return versions

    @classmethod
    def get_scripts_path(cls):
        return os.path.join(CodePaths.get_repo_path(), 'emmPipe', 'maya', 'scripts')

    @classmethod
    def get_plugin_path(cls):
        return os.path.join(CodePaths.get_repo_path(), 'emmPipe', 'maya', 'plug-ins')
    
    @classmethod
    def get_icons_path(cls):
        return os.path.join(CodePaths.get_repo_path(), 'emmPipe', 'maya', 'icons')
    
    @classmethod
    def get_prod_shelf_path(cls):
        return os.path.join(CodePaths.get_repo_path(), 'emmPipe', 'maya', 'shelves', 'prod')
    
    @classmethod
    def get_dev_shelf_path(cls):
        return os.path.join(CodePaths.get_repo_path(), 'emmPipe', 'maya', 'shelves', 'dev')


class UnrealEnginePaths():

    BASE_PATH = r'D:\Games'
    EXE_PATH =  r'D:\Games\UE_{}\Engine\Binaries\Win64\UnrealEditor.exe'

    @classmethod
    def get_exe_path(cls, version):
        return cls.EXE_PATH.format(version)

    @classmethod
    def get_version(cls):

        versions = [version.split('_')[-1] for version in os.listdir(cls.BASE_PATH) if version.startswith('UE_')]
        versions = sorted(versions, reverse=True)

        return versions
    
    @classmethod
    def get_scripts_path(cls):
        return os.path.join(CodePaths.get_repo_path(), 'emmPipe', 'unreal_engine', 'scripts')