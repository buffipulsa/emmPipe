
from typing import TypeVar

from rig.objects.object_data import DependencyNodeData, DagNodeData

T = TypeVar('T', bound=BaseObject)

class BaseObject:

    def __init__(self) -> None: ...

    #... PUBLIC METHODS ...#
    @classmethod
    def from_data(cls: type[T], meta_node: str, data: dict) -> T: ...

    #... PRIVATE METHODS ...#
    def _add_module(self, name: str, parent: str, vis_switch: bool) -> DagNodeData: ...

    def _create_meta_data(self) -> dict: ...
    
    def _create_meta_node(self, name: str) -> None: ...

    #... PROPERTIES ...#
    @property
    def meta_node(self) -> DependencyNodeData: ...
    
    @meta_node.setter
    def meta_node(self, value: str) -> None: ...
