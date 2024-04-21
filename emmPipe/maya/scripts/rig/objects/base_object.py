
from rig.objects.object_data import DependencyNodeData, MetaNode
from dev.utils import convert_str_to_list
from dev.logging.logger import Logger

class BaseObject:
    """
    Base class for objects in the rig.
    """
    def __init__(self) -> None:
        
        self.logger = Logger(__name__)
        self.logger.level = 'DEBUG'

    def create_meta_data(self):
        """
        Creates and returns the metadata dictionary for the object.
        """
        self.data = {}
        self.data['class_module'] = str(self.__class__.__module__)
        self.data['class_name'] = str(self.__class__.__name__)

        self.logger.info(f'Creating metadata for {self.__class__.__name__} object.')

        return self.data
    
    def create_meta_node(self):
        """
        Creates the meta node for the object.
        """
        self._meta_node = DependencyNodeData(MetaNode(self._name, self.data).name)

    @classmethod
    def from_data(cls, meta_node, data):
        """
        Creates an instance of the class from the given metadata node and data.
        """
        cls.instance = cls(*convert_str_to_list(data['parameters']))
        cls.instance.meta_node = meta_node

        return cls.instance