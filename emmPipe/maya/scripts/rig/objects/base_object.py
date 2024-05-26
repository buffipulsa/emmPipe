
import maya.cmds as cmds

from rig.objects.object_data import DependencyNodeData, MetaNode, DagNodeData
from dev.utils import convert_str_to_list, combine_names
from dev.logging.logger import Logger

from rig.objects.object_data import DeserializeMetaNode

class BaseObject:
    """
    Base class for objects in the scene.

    Methods:
        Public:
        from_data(cls, meta_node, data): Creates an instance of the class using the provided data.
        
        Private:
        _add_module(name, parent=None, vis_switch=True): Adds a module to the scene.
        _create_meta_data(): Creates metadata for the object.
        _create_meta_node(name): Creates a meta node with the given name and assigns it to the `_meta_node` attribute.

    Properties:
        meta_node (str): The meta node associated with the instance.
    """
    def __str__(self):
        return f'{self._combined_name}'

    def __init__(self,name, side, desc, index=0) -> None:

        self._name = name
        self._side = side
        self._desc = desc
        self._index = index

        self._combined_name = combine_names(self._name, self._side, self._desc, self._index)

        self._meta_node = None
        self._meta_node_name = None

        return

    #... PUBLIC METHODS ...#
    def create(self):
        """
        Creates the object in the scene.

        Returns:
            None
        """
        self._create_meta_data()
        self._create_meta_node(self._combined_name)
        
        return
    
    @classmethod
    def rebuild(self, meta_node):

        self._meta_node = meta_node
    
    #... PRIVATE METHODS ...#
    def _create_meta_data(self):
        """
        Creates metadata for the object.

        Returns:
            dict: A dictionary containing the metadata.
        """
        self.data = {}
        self.data['class_module'] = str(self.__class__.__module__)
        self.data['class_name'] = str(self.__class__.__name__)

        self.data['parameters'] = repr(self)

        return self.data
    
    def _create_meta_node(self, name):
        """
        Creates a meta node with the given name and assigns it to the `_meta_node` attribute.

        Args:
            name (str): The name of the meta node.

        Returns:
            None
        """
        self._meta_node = DependencyNodeData(MetaNode(name, self.data).name)
        self._meta_node_name = self._meta_node.dependnode_fn.name()

        return

    def _add_module(self, name, parent=None, vis_switch=True):
        """
        Adds a module to the scene.

        Args:
            name (str): The name of the module.
            parent (DagNodeData, optional): The parent node to attach the module to. Defaults to None.
            vis_switch (bool, optional): Whether to create a visibility switch attribute on the parent node. Defaults to True.

        Returns:
            DagNodeData: The created module.
        """
        module = DagNodeData(cmds.createNode('transform', name=f'{name}'))

        if parent:
            cmds.parent(module.dag_path, parent.dag_path)

            if vis_switch:
                vis_name = f'{module.transform_fn.name()}_vis'
                cmds.addAttr(parent.dag_path, longName=vis_name, attributeType='bool', keyable=True)
                cmds.setAttr(f'{parent.dag_path}.{vis_name}', 1)

                cmds.connectAttr(f'{parent.dag_path}.{vis_name}', f'{module.dag_path}.visibility')

        return module

    #... PROPERTIES ...#
    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, value):
        self._name = value.lower()

    @property
    def side(self):
        return self._side
    
    @side.setter
    def side(self, value):
        self._side = value.lower()

    @property
    def desc(self):
        return self._desc
    
    @desc.setter
    def desc(self, value):
        self._desc = value.lower()

    @property
    def index(self):
        return self._index
    
    @index.setter
    def index(self, value):
        self._index = value

    @property
    def combined_name(self):
        return self._combined_name
    
    @combined_name.setter
    def combined_name(self, value):
        self._combined_name = value

    @property
    def meta_node(self):
        return self._meta_node
    
    @meta_node.setter
    def meta_node(self, value):
        self._meta_node = value

    @property
    def meta_node_name(self):
        return self._meta_node_name

    @meta_node_name.setter
    def meta_node_name(self, value):
        self._meta_node_name = value

