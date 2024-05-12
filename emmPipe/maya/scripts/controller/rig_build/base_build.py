
import maya.cmds as cmds

from rig.modules.base import RigContrainer

class BaseBuild:

    def __init__(self, path_object):
        """
        Initialize the BaseBuild instance.

        Args:
            path_object (PathObject): The path object.
        """
        self.path_object = path_object

    
    def new_scene(self):
        """
        Creates a new scene.
        """
        print('New Scene')
        cmds.file(new=True, force=True)

    def create_rig_container(self):

        rig_container = RigContrainer('test').create()
    
    def import_model(self):
        """
        Imports the model.
        """
        self.path_object.import_model_component()

    def import_blueprint(self):
        """
        Imports the blueprint.
        """
        self.path_object.import_blueprint_component()
        
    def data(self):
        """
        Returns the data object.
        
        Returns:
            CData: The data object.
        """
        data = {'new_scene': {'label': 'New Scene', 'func': self.new_scene, 'is_checked': True},
                'rig_container': {'label': 'Rig Container', 'func': self.create_rig_container, 'is_checked': True},
                'import_model': {'label': 'Import Model', 'func': self.import_model, 'is_checked': True},
                'import_blueprint': {'label': 'Import Blueprint', 'func': self.import_blueprint, 'is_checked': True}}

        return data