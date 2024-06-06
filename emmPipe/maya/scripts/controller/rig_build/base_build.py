
import os

import maya.cmds as cmds

from rig.modules.base import RigContrainer
from ui.main.widgets.rig_widget.modules_widget import ModulesWidget
from controller.meta_data.query import MetaDataQuery

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

    def show_blueprint_tool(self):

        if os.getenv('EMMPIPE_MODE') == 'Development':
            if cmds.workspaceControl(ModulesWidget.get_workspace_control_name(), q=True, exists=True):
                cmds.deleteUI(ModulesWidget.get_workspace_control_name())
        
                print(f'{ModulesWidget.get_workspace_control_name()} Deleted')
        
        ModulesWidget.display()
    
    def hide_blueprint_tool(self):

        if os.getenv('EMMPIPE_MODE') == 'Development':
            ModulesWidget.close()
        else:
            ModulesWidget.hide()
        
    def data(self):
        """
        Returns the data object.
        
        Returns:
            CData: The data object.
        """
        data = {'new_scene': {'label': 'New Scene', 'func': self.new_scene, 'is_checked': True,
                              'tool': None},
                'rig_container': {'label': 'Rig Container', 'func': self.create_rig_container, 'is_checked': True,
                                  'tool': None},
                'import_model': {'label': 'Import Model', 'func': self.import_model, 'is_checked': True,
                                 'tool': None},
                'import_blueprint': {'label': 'Import Blueprint', 'func': self.import_blueprint, 'is_checked': True,
                                     'tool': self.show_blueprint_tool, 'tool_hide': self.hide_blueprint_tool}}

        return data