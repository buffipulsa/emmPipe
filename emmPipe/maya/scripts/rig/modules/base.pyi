
from rig.objects.base_object import BaseObject
from rig.objects.object_data import DagNodeData

class RigContrainer(BaseObject):

    def __init__(self, name: str) -> None: ...

    #... PUBLIC METHODS ...#
    def create(self) -> RigContrainer: ...
    
    @classmethod
    def from_data(cls, meta_node: str, data: dict): ...

    #... PRIVATE METHODS ...#
    def _initialize_modules(self) -> None: ...

    def _create_controls(self) -> None: ...

    def _set_type_meta(self, value) -> None: ...

    #... PROPERTIES ...#
    @property
    def type(self) -> str: ...

    @type.setter
    def type(self, value) -> None: ...

    @property
    def name(self) -> str: ...

    @name.setter
    def name(self, value) -> None: ...
    
    @property
    def top_node(self) -> DagNodeData: ...
    
    @top_node.setter
    def top_node(self, value) -> None: ...
    
    @property
    def geometry(self) -> DagNodeData: ...
    
    @geometry.setter
    def geometry(self, value) -> None: ...
    
    @property
    def controls(self) -> DagNodeData: ...
    
    @controls.setter
    def controls(self, value) -> None: ...
    
    @property
    def modules(self) -> DagNodeData: ...
    
    @modules.setter
    def modules(self, value) -> None: ...


class RigModule(BaseObject):

    def __init__(self, name: str) -> None: ...

    #... PUBLIC METHODS ...#
    def create(self) -> RigModule: ...

    @classmethod
    def from_data(cls, meta_node: str, data: dict) -> RigModule: ...

    #... PRIVATE METHODS ...#
    def _initialize_modules(self) -> None: ...
    
    def _create_meta_data(self) -> dict: ...

    #... PROPERTIES ...#
    @property
    def name(self): ...
    
    @property
    def module(self) -> DagNodeData: ...
    
    @module.setter
    def module(self, value: DagNodeData) -> None: ...

    @property
    def systems(self) -> DagNodeData: ...
    
    @systems.setter
    def systems(self, value: DagNodeData) -> None: ...

    @property
    def constraints(self) -> DagNodeData: ...
    
    @constraints.setter
    def constraints(self, value: DagNodeData) -> None: ...

    @property
    def joints(self):
        return self._joints
    
    @joints.setter
    def joints(self, value):
        self._joints = value

    @property
    def fk(self):
        return self._fk
    
    @fk.setter
    def fk(self, value):
        self._fk = value

    @property
    def ik(self):
        return self._ik
    
    @ik.setter
    def ik(self, value):
        self._ik = value
    
    @property
    def par_constraints(self):
        return self._par_constraints
    
    @par_constraints.setter
    def par_constraints(self, value):
        self._par_constraints = value
    
    @property
    def point_constraints(self):
        return self._point_constraints
    
    @point_constraints.setter
    def point_constraints(self, value):
        self._point_constraints = value
    
    @property
    def orient_constraints(self):
        return self._orient_constraints
    
    @orient_constraints.setter
    def orient_constraints(self, value):
        self._orient_constraints = value
    
    @property
    def scale_constraints(self):
        return self._scale_constraints
    
    @scale_constraints.setter
    def scale_constraints(self, value):
        self._scale_constraints = value
