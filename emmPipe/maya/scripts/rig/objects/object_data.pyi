
from typing import Union

import maya.api.OpenMaya as om


class DependencyNodeData:

    def __init__(self, node=None) -> None: ...

    #... Private methods ...#
    def _check_if_dag_or_depend_node(self) -> None: ...

    def _get_m_obj(self) -> om.MObject: ...
    
    def _get_dependnode_fn(self) -> om.MFnDependencyNode: ...

    #... Properties ...#
    @property
    def m_obj(self) -> om.MObject: ...
    
    @property
    def dependnode_fn(self) -> om.MFnDependencyNode: ...

class DagNodeData(DependencyNodeData):

    def __init__(self, node=None) -> None: ...

    #... Private methods ...#
    def _check_if_dag_or_depend_node(self) -> None: ...

    def _get_dag_path(self) -> om.MDagPath: ...

    def _get_shapes(self) -> list: ...
        
    def _get_transform_fn(self) -> om.MFnTransform: ...

    def _get_shapes_fn(self) -> Union[om.MFnMesh, om.MFnNurbsCurve, om.MFnNurbsSurface]: ...
        
    def _get_vtx_component(self) -> om.MObject: ...
        
    def _get_vtx_ids(self) -> list: ...
        
    def _get_vtx_counts(self) -> int: ...

    #... Properties ...#
    @property
    def dag_path(self) -> om.MDagPath: ...
        
    @property
    def shapes(self) -> list: ...

    @property
    def transform_fn(self) -> om.MFnTransform: ...
    
    @property
    def shapes_fn(self) -> Union[om.MFnMesh, om.MFnNurbsCurve, om.MFnNurbsSurface]: ...

    @property
    def vtx_component(self) -> om.MObject: ...
    
    @property
    def vtx_ids(self) -> list: ...
    
    @property
    def vtx_counts(self) -> int: ...


class MetaNode:

    def __init__(self, name: str, data: dict) -> None: ...

    #... Public methods ...#
    @classmethod
    def rebuild(cls, meta_node: str) -> object: ...

    #... Private methods ...#
    def _create_attrs(self) -> None: ...

    #... Properties ...#
    @property
    def name(self) -> str: ...


    
class DeserializeMetaNode:

    def __init__(self, meta_node: str) -> None: ...

    #... Public methods ...#
    def rebuild(self) -> object: ...

    #... Private methods ...#
    def _deseriazlie_data(self) -> None: ...

    def _get_attribute_name(self, attr: om.MObject) -> str: ...
    
    def _deserialize_message_attr(self, attr: str) -> om.MDagPath: ...

    def _deserialize_typed_attr(self, attr: str) -> str: ...

    def _deserialize_numeric_attr(self, attr: str) -> float: ...
    
    def _get_class(self) -> str: ...

    #... Properties ...#
    @property
    def data(self) -> dict: ...